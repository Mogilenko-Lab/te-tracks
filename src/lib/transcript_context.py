"""Stream sparse transcript geometry and complete record context from a pinned annotation."""

from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
import csv
import gzip
from pathlib import Path
import re

from records_io import tsv_stream

CONTEXT_POLICY = {"start_envelope_upstream_bp": 10000, "start_envelope_downstream_bp": 2000,
                  "end_envelope_downstream_bp": 10000, "tie_rule": "keep all ties"}
CONTEXT_PATHS = {"tables/record_transcript_context.tsv.gz", "tables/record_context.tsv.gz"}
PAIR_COLUMNS = ("rmsk_record_id transcript_id gene_id gene_type transcript_type ensembl_canonical "
                "mrna_start_nf strand_relation pair_status exon_bp intron_bp utr5_bp utr3_bp body_bp "
                "gene_body_bp dist_start dist_end dist_exon_edge dist_gene_start dist_gene_end").split()
RECORD_COLUMNS = ("rmsk_record_id length_bp annotated exon_bp_any body_frac_max body_genes_same "
                  "body_genes_opposite nearest_exon_edge_bp nearest_gene_end_bp nearest_gene_end_strand "
                  "nearest_gene_start_bp nearest_gene_start_strand").split()
REASONS = "body nearest_start nearest_end nearest_exon_edge start_envelope end_envelope".split()


def union(intervals):
    merged = []
    for a, b in sorted(intervals):
        if merged and a <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def overlap(a, b, intervals):
    return sum(max(0, min(b, y) - max(a, x) + 1) for x, y in intervals)


def distance(a, b, point, strand="+"):
    return (a - point if point < a else b - point if point > b else 0) * (1 if strand == "+" else -1)


class Points:
    def __init__(self, pairs):
        groups = defaultdict(set)
        for position, owner in pairs:
            groups[position].add(owner)
        self.positions = sorted(groups)
        self.owners = [groups[p] for p in self.positions]

    def nearest(self, a, b):
        lo, hi = bisect_left(self.positions, a), bisect_right(self.positions, b)
        if lo < hi:
            return 0, set().union(*self.owners[lo:hi])
        candidates = [(abs(distance(a, b, self.positions[i])), self.owners[i])
                      for i in (lo - 1, hi) if 0 <= i < len(self.positions)]
        if not candidates:
            return None, set()
        best = min(d for d, _ in candidates)
        return best, set().union(*(owners for d, owners in candidates if d == best))

    def outside(self, a, b, left):
        i = bisect_left(self.positions, a) - 1 if left else bisect_right(self.positions, b)
        if 0 <= i < len(self.positions):
            return abs(distance(a, b, self.positions[i])), self.owners[i]
        return None, set()


class Intervals:
    """Index overlapping intervals with a centered tree and sorted crossing bounds."""
    def __init__(self, rows):
        self.center = None
        if not rows:
            return
        self.center = sorted((a + b) // 2 for a, b, _ in rows)[len(rows) // 2]
        left, right, crossing = [], [], []
        for row in rows:
            (left if row[1] < self.center else right if row[0] > self.center else crossing).append(row)
        crossing.sort()
        self.starts = [row[0] for row in crossing]
        self.by_start = [row[2] for row in crossing]
        crossing.sort(key=lambda row: row[1])
        self.ends = [row[1] for row in crossing]
        self.by_end = [row[2] for row in crossing]
        self.left, self.right = Intervals(left), Intervals(right)

    def query(self, a, b, found=None):
        if found is None:
            found = set()
        if self.center is None:
            return found
        if b < self.center:
            found.update(self.by_start[:bisect_right(self.starts, b)])
            self.left.query(a, b, found)
        elif a > self.center:
            found.update(self.by_end[bisect_left(self.ends, a):])
            self.right.query(a, b, found)
        else:
            found.update(self.by_start)
            self.left.query(a, b, found)
            self.right.query(a, b, found)
        return found


@dataclass
class Feature:
    chrom: str
    start: int
    end: int
    strand: str
    gene: str
    gene_type: str
    transcript_type: str = "NA"
    canonical: bool = False
    start_nf: bool = False
    exons: list = field(default_factory=list)
    cds: list = field(default_factory=list)
    utr: list = field(default_factory=list)
    utr5: list = field(default_factory=list)
    utr3: list = field(default_factory=list)

    @property
    def start_site(self):
        return self.start if self.strand == "+" else self.end

    @property
    def end_site(self):
        return self.end if self.strand == "+" else self.start


def read_annotation(gtf, alias_path):
    with open(alias_path) as stream:
        aliases = list(csv.DictReader(stream, delimiter="\t"))
    mapping = {r["chrom_gencode"]: r["chrom_ucsc"] for r in aliases}
    lengths = {r["chrom_ucsc"]: int(r["length_bp"]) for r in aliases}
    genes, transcripts, children, annotated = {}, {}, defaultdict(list), set()
    with gzip.open(gtf, "rt") as stream:
        for number, line in enumerate(stream, 1):
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) != 9 or f[0] not in mapping:
                raise ValueError(f"context GTF row {number}: invalid columns or contig")
            chrom, a, b = mapping[f[0]], int(f[3]), int(f[4])
            if not 1 <= a <= b <= lengths[chrom] or f[6] not in ("+", "-"):
                raise ValueError(f"context GTF row {number}: invalid bounds or strand")
            annotated.add(chrom)
            attrs = defaultdict(list)
            for key, value in re.findall(r'(\w+) "([^"\n]*)";', f[8]):
                attrs[key].append(value)
            if f[2] in ("gene", "transcript"):
                gene = attrs["gene_id"][0]
                item = Feature(chrom, a, b, f[6], gene, attrs.get("gene_type", ["NA"])[0],
                               attrs.get("transcript_type", ["NA"])[0],
                               "Ensembl_canonical" in attrs["tag"], "mRNA_start_NF" in attrs["tag"])
                target, key = (genes, gene) if f[2] == "gene" else (transcripts, attrs["transcript_id"][0])
                if key in target and target[key] != item:
                    raise ValueError(f"context conflicting annotation ID: {key}")
                target[key] = item
            elif f[2] in ("exon", "CDS", "UTR", "five_prime_utr", "three_prime_utr"):
                children[attrs["transcript_id"][0]].append((f[2], chrom, a, b, f[6], attrs["gene_id"][0]))
    for tid, rows in children.items():
        if tid not in transcripts:
            raise ValueError(f"context missing transcript: {tid}")
        t = transcripts[tid]
        for kind, chrom, a, b, strand, gene in rows:
            if (chrom, strand, gene) != (t.chrom, t.strand, t.gene) or not t.start <= a <= b <= t.end:
                raise ValueError(f"context child geometry differs: {tid}")
            getattr(t, {"exon": "exons", "CDS": "cds", "UTR": "utr",
                        "five_prime_utr": "utr5", "three_prime_utr": "utr3"}[kind]).append((a, b))
    for tid, t in transcripts.items():
        g = genes.get(t.gene)
        if g is None or (g.chrom, g.strand) != (t.chrom, t.strand) or not g.start <= t.start <= t.end <= g.end:
            raise ValueError(f"context transcript gene geometry differs: {tid}")
        t.exons, t.cds = union(t.exons), union(t.cds)
        if not t.exons:
            raise ValueError(f"context transcript has no exons: {tid}")
        if t.cds:
            lo, hi = t.cds[0][0], t.cds[-1][1]
            for a, b in t.utr:
                if a < lo:
                    (t.utr5 if t.strand == "+" else t.utr3).append((a, min(b, lo - 1)))
                if b > hi:
                    (t.utr3 if t.strand == "+" else t.utr5).append((max(a, hi + 1), b))
        t.utr5, t.utr3 = union(t.utr5), union(t.utr3)
    return genes, transcripts, annotated


class ContigContext:
    def __init__(self, genes, transcripts, policy):
        self.genes, self.transcripts = genes, transcripts
        self.body = Intervals([(t.start, t.end, tid) for tid, t in transcripts.items()])
        self.gene_body = Intervals([(g.start, g.end, gid) for gid, g in genes.items()])
        self.starts = Points([(t.start_site, tid) for tid, t in transcripts.items()])
        self.ends = Points([(t.end_site, tid) for tid, t in transcripts.items()])
        exons = [(a, b, tid) for tid, t in transcripts.items() for a, b in t.exons]
        self.exons = Intervals(exons)
        self.edges = Points([(p, tid) for a, b, tid in exons for p in (a, b)])
        self.exon_union = union([(a, b) for a, b, _ in exons])
        self.exon_union_ends = [b for a, b in self.exon_union]
        starts, ends = [], []
        for tid, t in transcripts.items():
            up, down = policy["start_envelope_upstream_bp"], policy["start_envelope_downstream_bp"]
            starts.append((t.start_site - (up if t.strand == "+" else down),
                           t.start_site + (down if t.strand == "+" else up), tid))
            down = policy["end_envelope_downstream_bp"]
            ends.append((t.end_site if t.strand == "+" else t.end_site - down,
                         t.end_site + down if t.strand == "+" else t.end_site, tid))
        self.start_envelope, self.end_envelope = Intervals(starts), Intervals(ends)
        self.gene_sites = {(kind, strand): Points([(getattr(g, kind + "_site"), gid)
                            for gid, g in genes.items() if g.strand == strand])
                           for kind in ("start", "end") for strand in ("+", "-")}

    def outside_gene(self, a, b, strand, kind):
        candidates = []
        for gs in ("+", "-"):
            d, owners = self.gene_sites[(kind, gs)].outside(a, b, (kind == "end") == (gs == "+"))
            if owners:
                candidates.append((d, "same" if gs == strand else "opposite"))
        if not candidates:
            return "NA", "NA"
        best = min(d for d, _ in candidates)
        relations = {relation for d, relation in candidates if d == best}
        return best, ";".join(r for r in ("same", "opposite") if r in relations)

    def rows(self, record):
        rid, a, b, strand = record.rmsk_record_id, record.start_1, record.end_1, record.strand
        exonic = self.exons.query(a, b)
        edge_distance, nearest_edges = (0, exonic) if exonic else self.edges.nearest(a, b)
        reasons = [self.body.query(a, b), self.starts.nearest(a, b)[1], self.ends.nearest(a, b)[1],
                   nearest_edges, self.start_envelope.query(a, b), self.end_envelope.query(a, b)]
        pairs = []
        for tid in sorted(set().union(*reasons)):
            t = self.transcripts[tid]
            g = self.genes[t.gene]
            exon_bp = overlap(a, b, t.exons)
            body_bp = overlap(a, b, [(t.start, t.end)])
            edge = 0 if exon_bp else min(abs(distance(a, b, p)) for x, y in t.exons for p in (x, y))
            pairs.append([rid, tid, t.gene, t.gene_type, t.transcript_type,
                          str(t.canonical).lower(), str(t.start_nf).lower(),
                          "same" if t.strand == strand else "opposite",
                          ";".join(reason for reason, owners in zip(REASONS, reasons) if tid in owners),
                          exon_bp, body_bp - exon_bp, overlap(a, b, t.utr5), overlap(a, b, t.utr3), body_bp,
                          overlap(a, b, [(g.start, g.end)]), distance(a, b, t.start_site, t.strand),
                          distance(a, b, t.end_site, t.strand), edge,
                          distance(a, b, g.start_site, g.strand), distance(a, b, g.end_site, g.strand)])
        bodies = [self.genes[gid] for gid in self.gene_body.query(a, b)]
        exon_bp_any = 0
        i = bisect_left(self.exon_union_ends, a)
        while i < len(self.exon_union) and self.exon_union[i][0] <= b:
            x, y = self.exon_union[i]
            exon_bp_any += min(b, y) - max(a, x) + 1
            i += 1
        rollup = [rid, b - a + 1, "true", exon_bp_any,
                  max((overlap(a, b, [(g.start, g.end)]) for g in bodies), default=0) / (b - a + 1),
                  sum(g.strand == strand for g in bodies), sum(g.strand != strand for g in bodies),
                  edge_distance if edge_distance is not None else "NA",
                  *self.outside_gene(a, b, strand, "end"), *self.outside_gene(a, b, strand, "start")]
        return pairs, rollup


class Context:
    def __init__(self, gtf, alias_path, policy):
        genes, transcripts, self.annotated = read_annotation(gtf, alias_path)
        self.contigs = {chrom: ContigContext({k: g for k, g in genes.items() if g.chrom == chrom},
                                            {k: t for k, t in transcripts.items() if t.chrom == chrom}, policy)
                        for chrom in sorted(self.annotated)}

    def rows(self, records):
        for record in records.itertuples(index=False):
            if record.chrom not in self.annotated:
                yield [], [record.rmsk_record_id, record.end_1 - record.start_1 + 1, "false", *(["NA"] * 9)]
            else:
                yield self.contigs[record.chrom].rows(record)


def write_context(parent_dir, child_dir, gtf, policy, chrom=None):
    from gene_child import record_batches
    context = Context(gtf, child_dir / "tables/contig_aliases.tsv", policy)
    counts = [0, 0]
    with tsv_stream(child_dir / "tables/record_transcript_context.tsv.gz") as pairs, \
            tsv_stream(child_dir / "tables/record_context.tsv.gz") as records:
        pair_writer = csv.writer(pairs, delimiter="\t", lineterminator="\n")
        record_writer = csv.writer(records, delimiter="\t", lineterminator="\n")
        pair_writer.writerow(PAIR_COLUMNS)
        record_writer.writerow(RECORD_COLUMNS)
        for batch in record_batches(parent_dir):
            if chrom:
                batch = batch.loc[batch.chrom == chrom]
            for relation, rollup in context.rows(batch):
                pair_writer.writerows(relation)
                record_writer.writerow(rollup)
                counts[0] += len(relation)
                counts[1] += 1
    print(f"context rows: pairs={counts[0]} records={counts[1]}", flush=True)
    return counts


def verify_context(child_dir, parent_dir, gtf, policy):
    from gene_child import record_batches
    from manifest import require
    context = Context(gtf, child_dir / "tables/contig_aliases.tsv", policy)
    with gzip.open(child_dir / "tables/record_transcript_context.tsv.gz", "rt") as pairs, \
            gzip.open(child_dir / "tables/record_context.tsv.gz", "rt") as records:
        pair_reader, record_reader = csv.reader(pairs, delimiter="\t"), csv.reader(records, delimiter="\t")
        require(next(pair_reader) == PAIR_COLUMNS, "transcript context columns differ")
        require(next(record_reader) == RECORD_COLUMNS, "record context columns differ")
        for batch in record_batches(parent_dir):
            for relation, rollup in context.rows(batch):
                require(next(record_reader, None) == list(map(str, rollup)), "record context geometry differs")
                for row in relation:
                    require(next(pair_reader, None) == list(map(str, row)), "transcript context geometry differs")
        require(next(pair_reader, None) is None and next(record_reader, None) is None, "context extra rows")

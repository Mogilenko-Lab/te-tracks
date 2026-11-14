# Transcript geometry fixture

`annotation.gtf` defines fourteen transcripts on nine contigs. A and B have two exons and
oriented UTRs; C and D overlap on opposite strands; E and F have 3′ ends bordering a shared gap.
`records.tsv` defines exon, intron, strand, overlapping-gene, downstream-envelope,
partial-body, between-gene and unannotated-contig cases.
`record_context.tsv` and `pair_geometry.tsv` are hand-authored answers in record order.
A's end is base 300: base 10300 belongs to its end envelope and base 10301 lies beyond it.
The shared gap at base 250 ties E and F at starts, ends and exon edges.
The fixture check supplies literal metadata expectations beside the geometry answers.

G and H share a gene span with a gap between their transcript bodies. I and J have 5′ starts bordering a
shared gap, tying at upstream gene starts. Start-envelope boundary records cover +2000
on the plus strand and −10000 on the minus strand, with adjacent outside records.

A whole-body record spans both exons and their intron. A record overlapping G and H
counts their shared gene once and keeps both zero-distance exon ties.

`contig_aliases.tsv` supplies contig lengths, including chr1’s last base, 50000.
The endpoint records at 1 and 50000 have start distances −99 and +49900 to A.
K and L are plus-strand genes [100,300] and [200,400]; [230,239] overlaps both bodies.
M spans [20100,20300] on the plus strand: bases 10100 and 10099 test the upstream start boundary.
N has the same span on the minus strand: bases 18300 and 18299 test the downstream start boundary;
bases 10100 and 10099 test its downstream end boundary. Each boundary includes its endpoint.
The two answer tables contain literal expected values derived from these definitions.

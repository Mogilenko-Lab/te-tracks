"""One-pass audit of UCSC mm39 rmsk against te-tracks' declared expectations.

Writes tab-separated reports under report/. Every number here is measured from the
downloaded source, so it can be compared line-by-line against config/mm39.env.
"""
import gzip, sys, collections, json
import pandas as pd

SRC = "/workspaces/Meta-Aging/_scratch/te-tracks-audit/source/rmsk.txt.gz"
OUT = "/workspaces/Meta-Aging/_scratch/te-tracks-audit/report"
cols = ["bin","swScore","milliDiv","milliDel","milliIns","genoName","genoStart","genoEnd",
        "genoLeft","strand","repName","repClass","repFamily","repStart","repEnd","repLeft","id"]
df = pd.read_csv(SRC, sep="\t", header=None, names=cols, dtype={"id": str, "genoName": str},
                 low_memory=False)
n_all = len(df)
print("rows total", n_all)

# --- the declared rule --------------------------------------------------------------
TE_CLASSES = "SINE LTR LINE DNA Satellite Retroposon Unknown RC Unspecified DNA?".split()
keep_cls = df.repClass.isin(TE_CLASSES)
excl_trna = df.repFamily.str.startswith("tRNA")
te = df[keep_cls & ~excl_trna]
print("rule loci", len(te), "expect 3799629")
print("rule contigs", te.genoName.nunique(), "expect 59")
print("rule subfamilies", te.repName.nunique(), "expect 1225")
trip = te.groupby(["repName","repFamily","repClass"]).size()
print("rule triples", len(trip), "expect 1245")

# --- per class census, full source and under the rule --------------------------------
full_cls = df.repClass.value_counts().rename("n_source")
rule_cls = te.repClass.value_counts().rename("n_rule")
pd.concat([full_cls, rule_cls], axis=1).fillna(0).astype(int).to_csv(f"{OUT}/class_census.tsv", sep="\t")

# --- multiplicity: repName with >1 (family, class) triple -----------------------------
mult = trip.reset_index(name="n_loci")
counts_per_name = mult.groupby("repName").size()
multi_names = counts_per_name[counts_per_name > 1].index
mult_rows = mult[mult.repName.isin(multi_names)].sort_values(["repName","repFamily","repClass"])
mult_rows.to_csv(f"{OUT}/subfamily_multiplicity.tsv", sep="\t", index=False)
print("repNames with >1 triple under rule:", len(multi_names), "affecting", int(mult_rows.n_loci.sum()), "loci")
# same on the full source (before any filter)
trip_all = df.groupby(["repName","repFamily","repClass"]).size().reset_index(name="n_loci")
cpn_all = trip_all.groupby("repName").size()
print("repNames with >1 triple in full source:", int((cpn_all > 1).sum()))

# --- the id column ---------------------------------------------------------------------
idv = df["id"].astype(str)
print("id distinct values:", idv.nunique())
print("id value sample:", idv.value_counts().head(12).to_dict())
print("id max strlen:", idv.str.len().max())

# --- consensus coordinates -------------------------------------------------------------
# For + strand rmsk stores repStart>0, repLeft<=0; for - strand repStart is negative (=-repLeft)
print("repStart <0 fraction:", round((df.repStart < 0).mean(), 4),
      " repLeft <0 fraction:", round((df.repLeft < 0).mean(), 4))
print("strand values:", df.strand.value_counts().to_dict())

# --- alternative universes (named policy candidates) ----------------------------------
policies = {
  "legacy_bulk_compatible": keep_cls & ~excl_trna,
  "interspersed_te_with_satellite": keep_cls,
  "interspersed_te_no_satellite": keep_cls & (df.repClass != "Satellite"),
  "retrotransposon_only": df.repClass.isin(["LINE","SINE","LTR","Retroposon"]),
  "satellite_only": df.repClass == "Satellite",
  "structural_rna_classes": df.repClass.isin(["tRNA","rRNA","scRNA","snRNA","srpRNA"]),
  "simple_low_complexity": df.repClass.isin(["Simple_repeat","Low_complexity"]),
}
rows = []
for name, m in policies.items():
    sub = df[m]
    rows.append(dict(policy=name, n_loci=len(sub), n_subfamilies=sub.repName.nunique(),
                     n_triples=len(sub.groupby(["repName","repFamily","repClass"]).size()),
                     total_bp=int((sub.genoEnd - sub.genoStart).sum())))
pd.DataFrame(rows).to_csv(f"{OUT}/policy_universes.tsv", sep="\t", index=False)
print(pd.DataFrame(rows).to_string(index=False))

# --- tRNA-prefixed families: what exactly is dropped -----------------------------------
trna_fam = df[keep_cls & excl_trna].groupby(["repClass","repFamily","repName"]).size().reset_index(name="n")
trna_fam.to_csv(f"{OUT}/trna_prefix_dropped.tsv", sep="\t", index=False)
print(trna_fam.to_string(index=False))

# --- coordinate-key uniqueness for the selfdesc locus_id -------------------------------
key = te.repName + "|" + te.genoName + ":" + (te.genoStart+1).astype(str) + "-" + te.genoEnd.astype(str) + "|" + te.strand
print("selfdesc locus_id unique:", key.nunique(), "of", len(key))
coord_key = te.genoName + ":" + te.genoStart.astype(str) + "-" + te.genoEnd.astype(str) + ":" + te.strand
print("coordinate-only key unique:", coord_key.nunique(), "of", len(coord_key))
# overlapping/nested records within the rule set
te_s = te.sort_values(["genoName","genoStart","genoEnd"])
prev_end = te_s.groupby("genoName").genoEnd.cummax().shift(1)
same_chr = te_s.genoName.eq(te_s.genoName.shift(1))
overl = (same_chr & (te_s.genoStart < prev_end)).sum()
print("records whose start lies inside an earlier record's span (same contig):", int(overl))

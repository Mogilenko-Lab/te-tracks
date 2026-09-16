"""Label-level reconciliation: TEtranscripts packaged GRCm39 GTF vs the rmsk rule set.

Join on (chrom, start, end, strand) after mapping Ensembl contig names to UCSC through chromAlias,
then list every record whose subfamily/family/class label differs. Writes alias and conflict tables.
"""
import gzip, re, pandas as pd
OUT="report"
alias=pd.read_csv("source/chromAlias.txt",sep="\t",comment=None)
alias.columns=[c.lstrip("# ") for c in alias.columns]
ens2ucsc=dict(zip(alias["ensembl"],alias["ucsc"]))
# packaged GTF
rows=[]
pat=re.compile(r'gene_id "([^"]+)"; transcript_id "([^"]+)"; family_id "([^"]+)"; class_id "([^"]+)"')
with gzip.open("/data2/users/shared/refcache/mm39/mm39_20260911/GRCm39_Ensembl_rmsk_TE.gtf.gz","rt") as fh:
    for l in fh:
        if l[0]=="#": continue
        p=l.rstrip("\n").split("\t")
        m=pat.search(p[8])
        rows.append((p[0],int(p[3]),int(p[4]),p[6],m.group(1),m.group(2),m.group(3),m.group(4)))
pk=pd.DataFrame(rows,columns=["ens_chrom","start","end","strand","pk_subfamily","pk_transcript","pk_family","pk_class"])
pk["chrom"]=pk.ens_chrom.map(ens2ucsc)
print("packaged records",len(pk)," unmapped contigs:",pk.chrom.isna().sum(), pk[pk.chrom.isna()].ens_chrom.unique()[:10])
print("packaged strand values:", pk.strand.value_counts().to_dict())
print("packaged transcript_id grammar sample:", pk.pk_transcript.head(3).tolist())
# rmsk rule set
cols=["bin","swScore","milliDiv","milliDel","milliIns","genoName","genoStart","genoEnd","genoLeft","strand","repName","repClass","repFamily","repStart","repEnd","repLeft","id"]
r=pd.read_csv("source/rmsk.txt.gz",sep="\t",header=None,names=cols,dtype={"id":str},low_memory=False)
TE="SINE LTR LINE DNA Satellite Retroposon Unknown RC Unspecified DNA?".split()
te=r[r.repClass.isin(TE)&~r.repFamily.str.startswith("tRNA")].copy()
te["start"]=te.genoStart+1; te=te.rename(columns={"genoName":"chrom","genoEnd":"end"})
j=pk.merge(te[["chrom","start","end","strand","repName","repFamily","repClass"]],on=["chrom","start","end","strand"],how="outer",indicator=True)
print("join:", j._merge.value_counts().to_dict())
# strand-agnostic check for the unmatched
un=j[j._merge!="both"]
if len(un):
    print("unmatched sample:"); print(un.head(10).to_string())
b=j[j._merge=="both"]
mis=b[(b.pk_subfamily!=b.repName)|(b.pk_family!=b.repFamily)|(b.pk_class!=b.repClass)]
print("records with any label difference:", len(mis))
# alias table: distinct (packaged label -> rmsk label) pairs with counts, per level
for lvl,(a,c) in {"subfamily":("pk_subfamily","repName"),"family":("pk_family","repFamily"),"class":("pk_class","repClass")}.items():
    d=b[b[a]!=b[c]].groupby([a,c]).size().reset_index(name="n_records").sort_values("n_records",ascending=False)
    d.to_csv(f"{OUT}/alias_{lvl}.tsv",sep="\t",index=False)
    print(f"--- {lvl}: {len(d)} distinct label pairs, {int(d.n_records.sum())} records"); print(d.head(12).to_string(index=False))
# class conflicts in full
cc=b[b.pk_class!=b.repClass][["chrom","start","end","strand","repName","repFamily","repClass","pk_subfamily","pk_family","pk_class"]]
cc.to_csv(f"{OUT}/conflict_class.tsv",sep="\t",index=False); print("class conflicts:"); print(cc.to_string(index=False))
# family conflicts that are NOT the Unknown-relabel and NOT the v->. substitution
fam=b[(b.pk_family!=b.repFamily)&(b.repFamily!="Unknown")&(b.pk_family.str.replace(".","v",regex=False)!=b.repFamily)]
print("family differences beyond Unknown-relabel and v->. :", len(fam)); print(fam.groupby(["repName","repFamily","pk_family"]).size().head(20).to_string())

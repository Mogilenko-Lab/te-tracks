"""Compare UCSC rmsk.txt against the raw RepeatMasker .out for mm39.

Answers: does .out carry a real fragment-linkage ID; how many insertions span several
fragments; what the trailing '*' (overlapped, lower-scoring) flag marks; do the two files
hold the same record set (IRescue reads .out.gz, te-tracks reads rmsk.txt.gz).
"""
import gzip, re, collections
import pandas as pd

OUT="report"
rows=[]
with gzip.open("source/mm39.fa.out.gz","rt") as fh:
    for i,line in enumerate(fh):
        if i<3: continue
        p=line.split()
        if len(p)<15: continue
        star = (len(p)>=16 and p[15]=="*")
        rows.append((int(p[0]),float(p[1]),p[4],int(p[5]),int(p[6]),p[8],p[9],p[10],p[11],p[12],p[13],int(p[14]),star))
o=pd.DataFrame(rows,columns=["sw","div","chrom","beg","end","strand","name","cf","rbeg","rend","rleft","id","star"])
print(".out records", len(o))
print(".out distinct id", o.id.nunique(), " max id", o.id.max())
per=o.groupby(["chrom","id"]).size()
print("fragments per (chrom,id): 1 ->", int((per==1).sum()), " 2 ->", int((per==2).sum()), " 3+ ->", int((per>=3).sum()))
print("records with '*' overlap flag:", int(o.star.sum()))
# does id restart per chromosome?
first_ids = o.groupby("chrom").id.min()
print("id min per chrom sample:", first_ids.head(5).to_dict())
o[["cls","fam"]] = o.cf.str.split("/",n=1,expand=True)
o["fam"]=o.fam.fillna(o.cls)
# compare record sets with rmsk.txt on (chrom, 1-based start, end, name)
cols=["bin","swScore","milliDiv","milliDel","milliIns","genoName","genoStart","genoEnd","genoLeft","strand","repName","repClass","repFamily","repStart","repEnd","repLeft","id"]
r=pd.read_csv("source/rmsk.txt.gz",sep="\t",header=None,names=cols,dtype={"id":str},low_memory=False)
kr=set(zip(r.genoName,r.genoStart+1,r.genoEnd,r.repName))
ko=set(zip(o.chrom,o.beg,o.end,o.name))
print("rmsk.txt records", len(r), " .out records", len(o))
print("in both", len(kr&ko), " rmsk-only", len(kr-ko), " out-only", len(ko-kr))
# rmsk.txt id (char(1)) vs .out id: is rmsk.id == last digit of out.id?
m = o.merge(r[["genoName","genoStart","genoEnd","repName","id"]].rename(columns={"genoName":"chrom","genoEnd":"end","repName":"name","id":"ucsc_id"}).assign(beg=lambda d:d.genoStart+1),
            on=["chrom","beg","end","name"], how="inner")
print("ucsc char(1) id == last digit of .out id:", round((m.ucsc_id == (m.id % 10).astype(str)).mean(),4))
# multi-fragment insertions under the te-tracks class rule
TE="SINE LTR LINE DNA Satellite Retroposon Unknown RC Unspecified DNA?".split()
ote=o[o.cls.isin(TE)]
per_te=ote.groupby(["chrom","id"]).size()
print("TE-class (chrom,id) groups:", len(per_te), " multi-fragment:", int((per_te>1).sum()), " fragments in multi:", int(per_te[per_te>1].sum()))
# do fragments in one id share name? mixed names = nested/different elements sharing an ID (shouldn't) 
nm=ote.groupby(["chrom","id"]).name.nunique()
print("multi-fragment ids with >1 repName:", int((nm>1).sum()))
per_te[per_te>1].reset_index(name="n_frag").groupby("n_frag").size().to_csv(f"{OUT}/out_fragments_per_insertion.tsv",sep="\t",header=["n_insertions"])
o.star.groupby(o.cls).sum().to_csv(f"{OUT}/out_star_by_class.tsv",sep="\t",header=["n_star"])

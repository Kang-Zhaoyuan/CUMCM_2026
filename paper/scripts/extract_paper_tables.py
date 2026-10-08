"""Read existing calculation workbooks and emit LaTeX tables as JSON."""
from pathlib import Path
import json
import numpy as np
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/"code"/"results"
OUT={}
def load(path):
    book=load_workbook(path,read_only=True,data_only=True)
    ans={s.title:list(s.values) for s in book}
    book.close()
    return ans
def table(name,caption,label,header,rows,group=None,note=None):
    cols=len(header)
    lines=[r"\begin{table}[!htbp]\centering\small",
           r"\caption{"+caption+r"}\label{"+label+"}",
           r"\renewcommand{\arraystretch}{1.15}",
           r"\begin{tabular*}{0.96\textwidth}{@{\extracolsep{\fill}}"+"c"*cols+"}",
           r"\toprule"]
    if group:
        start,end,text=group
        parts=[""]*(start-1)+[r"\multicolumn{"+str(end-start+1)+r"}{c}{"+text+"}"]+[""]*(cols-end)
        lines+=[" & ".join(parts)+r"\\",r"\cmidrule(lr){"+f"{start}-{end}"+"}"]
    lines+=[" & ".join(header)+r"\\\midrule"]
    lines+=[" & ".join(row)+r"\\" for row in rows]
    lines += [r"\bottomrule",r"\end{tabular*}"]
    if note: lines += [r"\par\smallskip{\footnotesize "+note+"}"]
    lines += [r"\end{table}"]
    OUT[name]="\n".join(lines)+"\n"
for q in range(1,5):
    data=load(RESULTS/f"result{q}.xlsx")
    for index,(sheet,rows) in enumerate(data.items()):
        header=rows[0]
        columns=[header.index(p) for p in [0,.5,1,1.5,2]]
        if q==1: times=[100,300,600,900,1200,1500,1800]
        elif q==2: times=[1800,3600,5400,7200,9000,10800]
        else: times=list(range(21600,int(rows[-1][0])+1,21600))+[rows[-1][0]]
        keyed={row[0]:row for row in rows[1:]}
        values=[]
        for t in times:
            row=keyed[t]
            vals=[f"{t if q==1 else t/3600:.4f}"]
            vals+=["---" if row[c] is None else f"{row[c]:.4f}" for c in columns]
            if q==4: vals+=[f"{row[header.index('药材表面')]:.4f}",f"{row[header.index('半径/cm')]:.4f}"]
            values.append(vals)
        temp=index==0 and q<3
        unit=r"$ {}^\circ\mathrm{C}$" if temp else r"$\mathrm{kg/kg}$"
        caption={1:"预热阶段中部截面的",2:"初始3小时中部截面的",3:"固定几何下中部截面的",4:"径向收缩下中部截面的"}[q]+("温度" if temp else "干基含水率")+"，单位："+unit
        name=f"q{q}-"+("temperature" if temp else "moisture")
        heads=["时间/"+("s" if q==1 else "h"),"0","0.5","1.0","1.5","2.0"]
        if q==4: heads+=["药材表面","半径/cm"]
        note=None
        if q==4: note="注：含水率单位为kg/kg，半径单位为cm；“---”表示该位置已在药材外部，末行为烘干结束时刻。"
        elif q==3: note="注：末行为烘干结束时刻，时间单位为h。"
        table(name,caption,"tab:"+name,heads,values,(2,7 if q==4 else 6,"到药材轴线的距离/cm"),note)
folder=ROOT/"code"/"results"
reference=load(next(folder.glob("result1_nr160_nz160_*.xlsx")))
output=[]
for n in [60,80,100,120,140,160]:
    candidate=load(next(folder.glob(f"result1_nr{n}_nz{n}_*.xlsx")))
    errs=[]
    for key in reference:
        ref=np.array(reference[key][1:],float)[:,1:]
        val=np.array(candidate[key][1:],float)[:,1:]
        errs.append(float(np.max(np.abs(ref-val))))
    output.append([f"$ {n}\\times {n}$",*[f"{v:.4f}" for v in errs]])
table("q1-grid","问题一各网格相对参考网格的最大差异","tab:q1-grid",
      ["网格区间数",r"温度最大差/$ {}^\circ\mathrm{C}$","含水率最大差/(kg/kg)"],output,
      note="注：比较现有四位小数导出值，参考网格为$160\\times160$；表中差异受导出精度限制。")
print(json.dumps(OUT,ensure_ascii=False))


"""Add batchId to frontend data summary table and CSV export."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"

PATCHES: list[tuple[str, str, str]] = [
    (
        "csv export",
        'pe=(await kx(Y)).records.map(se=>({sampleName:se.sampleName,temperature:se.temperature,'
        'weight:se.weight,length:se.length,width:se.width,height:se.height,waterCutWidth:se.waterCutWidth,'
        'timestamp:Uo(se.recordedAt)})),ae=[["名称","温度(°C)","重量(g)","长(mm)","宽(mm)","高(mm)",'
        '"水切宽度(mm)","时间"].join(","),...pe.map(se=>[se.sampleName,se.temperature,se.weight,'
        "se.length,se.width,se.height,se.waterCutWidth,se.timestamp].join(\",\"))]",
        'pe=(await kx(Y)).records.map(se=>({batchId:se.batchId??"",sampleName:se.sampleName,'
        'temperature:se.temperature,weight:se.weight,length:se.length,width:se.width,height:se.height,'
        'waterCutWidth:se.waterCutWidth,timestamp:Uo(se.recordedAt)})),ae=[["批次号","名称","温度(°C)",'
        '"重量(g)","长(mm)","宽(mm)","高(mm)","水切宽度(mm)","时间"].join(","),...pe.map(se=>[se.batchId,'
        "se.sampleName,se.temperature,se.weight,se.length,se.width,se.height,se.waterCutWidth,"
        "se.timestamp].join(\",\"))]",
    ),
    (
        "load records",
        "r(he.records.map(ae=>({id:ae.id,sampleName:ae.sampleName,type:ae.recordType,temperature:ae.temperature,"
        "weight:ae.weight,length:ae.length,width:ae.width,height:ae.height,waterCutWidth:ae.waterCutWidth,"
        "timestamp:Uo(ae.recordedAt)})))",
        "r(he.records.map(ae=>({id:ae.id,batchId:ae.batchId??\"\",sampleName:ae.sampleName,type:ae.recordType,"
        "temperature:ae.temperature,weight:ae.weight,length:ae.length,width:ae.width,height:ae.height,"
        "waterCutWidth:ae.waterCutWidth,timestamp:Uo(ae.recordedAt)})))",
    ),
    (
        "table header",
        'children:[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Xl,{size:13,className:"text-cyan-400"}),"名称"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Zo,{size:13,className:"text-orange-400"}),"温度 (°C)"]})})',
        'children:[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Xl,{size:13,className:"text-cyan-400"}),"批次号"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Xl,{size:13,className:"text-cyan-400"}),"名称"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Zo,{size:13,className:"text-orange-400"}),"温度 (°C)"]})})',
    ),
    (
        "table body",
        'children:n?m.jsx(Di,{children:m.jsx(Ft,{colSpan:8,className:"text-center text-cyan-300 py-8",children:"加载中..."})}):V.length===0?m.jsx(Di,{children:m.jsx(Ft,{colSpan:8,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map($=>m.jsxs(Di,{className:"border-cyan-500/20 hover:bg-slate-800/40 transition-all",children:[m.jsx(Ft,{className:"text-cyan-50",children:$.sampleName}),',
        'children:n?m.jsx(Di,{children:m.jsx(Ft,{colSpan:9,className:"text-center text-cyan-300 py-8",children:"加载中..."})}):V.length===0?m.jsx(Di,{children:m.jsx(Ft,{colSpan:9,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map($=>m.jsxs(Di,{className:"border-cyan-500/20 hover:bg-slate-800/40 transition-all",children:[m.jsx(Ft,{className:"text-cyan-200 font-medium",children:$.batchId||"-"}),m.jsx(Ft,{className:"text-cyan-50",children:$.sampleName}),',
    ),
]


def patch(content: str) -> str:
    for name, old, new in PATCHES:
        if new in content:
            continue
        if old not in content:
            raise RuntimeError(f"{name} patch point not found")
        content = content.replace(old, new, 1)
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

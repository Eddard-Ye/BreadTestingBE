"""Hide water-cut column on data summary when recipe.enableWaterCut is false."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"

PATCHES: list[tuple[str, str, str]] = [
    (
        "reorder B/F",
        'B=[{value:"temperature",label:"温度 (°C)"},{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},{value:"waterCutWidth",label:"水切宽度 (mm)"}],z=()=>{const $=e[d];if(!$)return[];const Y=[{value:"product",label:"成品"}];return $.enableBottomMeasurement&&Y.push({value:"bottom",label:"底片"}),$.enableMiddleMeasurement&&Y.push({value:"middle",label:"中片"}),Y},H=z();',
        'z=()=>{const $=e[d];if(!$)return[];const Y=[{value:"product",label:"成品"}];return $.enableBottomMeasurement&&Y.push({value:"bottom",label:"底片"}),$.enableMiddleMeasurement&&Y.push({value:"middle",label:"中片"}),Y},H=z(),F=!!(e[d]&&e[d].enableWaterCut&&b==="product"),B=[{value:"temperature",label:"温度 (°C)"},{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},...(F?[{value:"waterCutWidth",label:"水切宽度 (mm)"}]:[])];',
    ),
    (
        "reset chart metric",
        'E.useEffect(()=>{const $=z();!$.some(ie=>ie.value===b)&&$.length>0&&g($[0].value),j(1)},[d,b,P,e]);',
        'E.useEffect(()=>{const $=z();!$.some(ie=>ie.value===b)&&$.length>0&&g($[0].value),j(1)},[d,b,P,e]),E.useEffect(()=>{!F&&x==="waterCutWidth"&&S("weight")},[F,x]);',
    ),
    (
        "chart data",
        "高:parseFloat($.height)||0,水切宽度:parseFloat($.waterCutWidth)||0})).reverse()",
        "高:parseFloat($.height)||0,...(F?{水切宽度:parseFloat($.waterCutWidth)||0}:{})})).reverse()",
    ),
    (
        "csv export",
        'ae=[["批次号","名称","温度(°C)","重量(g)","长(mm)","宽(mm)","高(mm)","水切宽度(mm)","时间"].join(","),...pe.map(se=>[se.batchId,se.sampleName,se.temperature,se.weight,se.length,se.width,se.height,se.waterCutWidth,se.timestamp].join(","))].join(`',
        'ae=[["批次号","名称","温度(°C)","重量(g)","长(mm)","宽(mm)","高(mm)",...(F?["水切宽度(mm)"]:[]),"时间"].join(","),...pe.map(se=>[se.batchId,se.sampleName,se.temperature,se.weight,se.length,se.width,se.height,...(F?[se.waterCutWidth]:[]),se.timestamp].join(","))].join(`',
    ),
    (
        "table header",
        '}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:13,className:"text-pink-400"}),"水切宽度 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(If,{size:13,className:"text-cyan-300"}),"时间"]})})]})}),m.jsx(mM,{children:n?m.jsx(Di,{children:m.jsx(Ft,{colSpan:9,',
        '}),...(F?[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:13,className:"text-pink-400"}),"水切宽度 (mm)"]})})]:[]),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(If,{size:13,className:"text-cyan-300"}),"时间"]})})]})}),m.jsx(mM,{children:n?m.jsx(Di,{children:m.jsx(Ft,{colSpan:F?9:8,',
    ),
    (
        "empty colspan",
        'm.jsx(Di,{children:m.jsx(Ft,{colSpan:9,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map',
        'm.jsx(Di,{children:m.jsx(Ft,{colSpan:F?9:8,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map',
    ),
    (
        "table cell",
        'm.jsx(Ft,{className:"text-cyan-100",children:$.height||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.waterCutWidth||"-"}),m.jsx(Ft,{className:"text-cyan-300 text-sm",children:$.timestamp||"-"})]},$.id))})]})}),c>A&&',
        'm.jsx(Ft,{className:"text-cyan-100",children:$.height||"-"}),...(F?[m.jsx(Ft,{className:"text-cyan-100",children:$.waterCutWidth||"-"})]:[]),m.jsx(Ft,{className:"text-cyan-300 text-sm",children:$.timestamp||"-"})]},$.id))})]})}),c>A&&',
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

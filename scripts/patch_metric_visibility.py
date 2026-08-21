"""Patch frontend for per-type metric visibility (show value vs '-')."""

from __future__ import annotations

import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"
HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"

VIS_HELPERS = (
    "function VisM(e,t,r){"
    'const n=!!(e!=null&&e.enableRoundBread),a=!!(e!=null&&e.enableWaterCut),'
    'o=r==="waterCutWidth"||r==="water_cut_width"?"water_cut_width":r;'
    "if(n){"
    'if(t==="product")return o==="temperature"||o==="weight"||o==="height"||a&&o==="water_cut_width";'
    'return o==="length"||o==="height"}'
    'if(t==="product")return o==="temperature"||o==="weight"||o==="height"||a&&o==="water_cut_width";'
    'if(t==="bottom")return o==="length"||o==="width"||o==="height";'
    'return o==="temperature"||o==="weight"||o==="length"||o==="width"||o==="height"}'
    "function VisV(e,t,r,n){return VisM(e,t,r)&&(n!=null&&n!==\"\")?n:\"-\"}"
    "function MaskRec(e,t,r){"
    'const n=l1(e,t),a=(n==null?void 0:n.recordType)||"product",o={...r};'
    'for(const l of["temperature","weight","length","width","height","waterCutWidth"])'
    "VisM(e,a,l)||(o[l]=\"-\");return o}"
    "function LteVis(e,t,r){"
    "if(!e)return!1;"
    'const n=typeof r==="string"?r:((t&&l1(t,r)||{}).recordType||e.type||"product");'
    'for(const a of["temperature","weight","length","width","height","waterCutWidth"]){'
    "if(!VisM(t,n,a))continue;"
    'const o=a==="waterCutWidth"?e.waterCutWidth:e[a];'
    'if(o==null||o===""||o==="-")return!1}return!0}'
)


def _replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, got {count}")
    return content.replace(old, new)


def patch(content: str) -> str:
    if "function VisM(" in content:
        print("VisM already present")
        return content

    # Insert helpers after RBr
    old_rbr = 'function RBr(e,t){return!!(e!=null&&e.enableRoundBread)}'
    content = _replace_once(content, old_rbr, old_rbr + VIS_HELPERS, "Vis helpers")

    # Replace Lte/Bte
    old_lte = (
        "function Lte(e){return!!(e!=null&&e.temperature&&(e!=null&&e.weight)&&(e!=null&&e.length))}"
        "function Bte(e,t){let r=0;for(let n=0;n<t;n+=1)Lte(e[n])&&(r+=1);return r}"
    )
    new_lte = (
        "function Lte(e,t,r){return LteVis(e,t,r)}"
        "function Bte(e,t,r){let n=0;for(let a=0;a<t;a+=1)LteVis(e[a],r,a)&&(n+=1);return n}"
    )
    content = _replace_once(content, old_lte, new_lte, "Lte/Bte")

    # Bte call site with recipe
    content = _replace_once(
        content,
        "const st=$te(ge),bt=Bte(Ie,st);",
        "const st=$te(ge),bt=Bte(Ie,st,ge);",
        "Bte call",
    )

    # Board completion count
    content = _replace_once(
        content,
        "j=g.filter(k=>k.temperature&&k.weight&&k.length).length",
        "j=g.filter(k=>LteVis(k,n,k.type)).length",
        "board completion",
    )

    # Capture result masking
    old_cap = (
        "wr={temperature:Ke.temperature,weight:Ke.weight,height:Ke.height,"
        "length:Ke.length,width:ge&&RBr(ge,d)?Ke.length:Ke.width,"
        'waterCutWidth:Ie?Ke.waterCutMm:"0",previewName:Ke.fileName,'
        "timestamp:St.toLocaleString(\"zh-CN\"),recordedAt:BC(St)}"
    )
    new_cap = (
        "wr=MaskRec(ge,d,{temperature:Ke.temperature,weight:Ke.weight,height:Ke.height,"
        "length:Ke.length,width:ge&&RBr(ge,d)?Ke.length:Ke.width,"
        'waterCutWidth:Ie?Ke.waterCutMm:"0",previewName:Ke.fileName,'
        "timestamp:St.toLocaleString(\"zh-CN\"),recordedAt:BC(St)})"
    )
    content = _replace_once(content, old_cap, new_cap, "capture mask")

    # Full board cells (div)
    old_full_cells = (
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.temperature||"-"}),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.weight||"-"}),'
        "...(n!=null&&n.enableRoundBread?"
        '[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.length||"-"})]:'
        '[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.length||"-"}),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.width||"-"})]),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.height||"-"}),'
        '...(e?[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",'
        'children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),'
    )
    new_full_cells = (
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"temperature",k.temperature)}),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"weight",k.weight)}),'
        "...(n!=null&&n.enableRoundBread?"
        '[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"length",k.length)})]:'
        '[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"length",k.length)}),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"width",k.width)})]),'
        'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:VisV(n,k.type,"height",k.height)}),'
        '...(e?[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",'
        'children:VisV(n,k.type,"waterCutWidth",k.waterCutWidth)})]:[]),'
    )
    content = _replace_once(content, old_full_cells, new_full_cells, "full board cells")

    # Indirect table cells (Ft)
    old_ind_cells = (
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.temperature||"-"}),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.weight||"-"}),'
        "...(n!=null&&n.enableRoundBread?"
        '[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.length||"-"})]:'
        '[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.length||"-"}),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.width||"-"})]),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.height||"-"}),'
        '...(e?[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",'
        'children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),'
    )
    new_ind_cells = (
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"temperature",k.temperature)}),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"weight",k.weight)}),'
        "...(n!=null&&n.enableRoundBread?"
        '[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"length",k.length)})]:'
        '[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"length",k.length)}),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"width",k.width)})]),'
        'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:VisV(n,k.type,"height",k.height)}),'
        '...(e?[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",'
        'children:VisV(n,k.type,"waterCutWidth",k.waterCutWidth)})]:[]),'
    )
    content = _replace_once(content, old_ind_cells, new_ind_cells, "indirect board cells")

    # Summary metric dropdown filter
    old_metrics = (
        '_rb=!!(e[d]&&e[d].enableRoundBread);let B=[{value:"temperature",label:"温度 (°C)"},'
        '{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},'
        '{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},'
        '...(F?[{value:"waterCutWidth",label:"水切宽度 (mm)"}]:[])];'
        '_rb&&(B=B.filter($=>$.value!=="width").map($=>$.value==="length"?{value:"length",label:"直径 (mm)"}:$));'
    )
    new_metrics = (
        '_rb=!!(e[d]&&e[d].enableRoundBread);let B=[{value:"temperature",label:"温度 (°C)"},'
        '{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},'
        '{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},'
        '...(F?[{value:"waterCutWidth",label:"水切宽度 (mm)"}]:[])];'
        "B=B.filter($=>VisM(e[d],b,$.value));"
        '_rb&&(B=B.map($=>$.value==="length"?{value:"length",label:"直径 (mm)"}:$));'
    )
    content = _replace_once(content, old_metrics, new_metrics, "summary metrics")

    # Summary table body cells
    old_sum_row = (
        'm.jsx(Ft,{className:"text-cyan-100",children:$.temperature||"-"}),'
        'm.jsx(Ft,{className:"text-cyan-100",children:$.weight||"-"}),'
        "...(_rb?[m.jsx(Ft,{className:\"text-cyan-100\",children:$.length||\"-\"})]:"
        '[m.jsx(Ft,{className:"text-cyan-100",children:$.length||"-"}),'
        'm.jsx(Ft,{className:"text-cyan-100",children:$.width||"-"})]),'
    )
    # Need more context - include height and waterCut
    i = content.find(old_sum_row)
    if i < 0:
        # try without escape differences
        raise RuntimeError("summary row start not found")
    # extend to water cut / timestamp
    tail_start = i + len(old_sum_row)
    # find height cell after
    height_pat = 'm.jsx(Ft,{className:"text-cyan-100",children:$.height||"-"})'
    if not content[tail_start:].startswith(height_pat):
        raise RuntimeError(f"summary height unexpected: {content[tail_start:tail_start+120]!r}")
    rest = content[tail_start + len(height_pat) :]
    # optional water cut
    wc_pat = ',...(F?[m.jsx(Ft,{className:"text-cyan-100",children:$.waterCutWidth||"-"})]:[])'
    if rest.startswith(wc_pat):
        old_sum_full = old_sum_row + height_pat + wc_pat
        new_sum_full = (
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"temperature",$.temperature)}),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"weight",$.weight)}),'
            "...(_rb?[m.jsx(Ft,{className:\"text-cyan-100\",children:VisV(e[d],b,\"length\",$.length)})]:"
            '[m.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"length",$.length)}),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"width",$.width)})]),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"height",$.height)}),'
            '...(F?[m.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"waterCutWidth",$.waterCutWidth)})]:[])'
        )
    else:
        old_sum_full = old_sum_row + height_pat
        new_sum_full = (
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"temperature",$.temperature)}),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"weight",$.weight)}),'
            "...(_rb?[m.jsx(Ft,{className:\"text-cyan-100\",children:VisV(e[d],b,\"length\",$.length)})]:"
            '[m.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"length",$.length)}),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"width",$.width)})]),'
            'm.jsx(Ft,{className:"text-cyan-100",children:VisV(e[d],b,"height",$.height)})'
        )
    content = _replace_once(content, old_sum_full, new_sum_full, "summary table cells")

    # Confirm dialog Ute metric cards
    old_ute_full = (
        'u=[{icon:m.jsx(Zo,{size:14,className:"text-orange-400"}),label:"温度",value:`${n.temperature} °C`,color:"text-orange-300",outOfRange:y("temperature",n.temperature)},'
        '{icon:m.jsx(Jo,{size:14,className:"text-yellow-400"}),label:"重量",value:`${n.weight} g`,color:"text-yellow-300",outOfRange:y("weight",n.weight)},'
        "...(s?[{icon:m.jsx($f,{size:14,className:\"text-blue-400\"}),label:\"直径\",value:`${n.length} mm`,color:\"text-blue-300\",outOfRange:y(\"length\",n.length)}]:"
        '[{icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"长度",value:`${n.length} mm`,color:"text-blue-300",outOfRange:y("length",n.length)},'
        '{icon:m.jsx(Mf,{size:14,className:"text-purple-400"}),label:"宽度",value:`${n.width} mm`,color:"text-purple-300",outOfRange:y("width",n.width)}]),'
        '{icon:m.jsx(Rf,{size:14,className:"text-emerald-400"}),label:"高度",value:`${n.height} mm`,color:"text-emerald-300",outOfRange:y("height",n.height)},'
        '...o?[{icon:m.jsx(Df,{size:14,className:"text-pink-400"}),label:"水切宽度",value:`${n.waterCutWidth} mm`,color:"text-pink-300",outOfRange:y("waterCutWidth",n.waterCutWidth)}]:[],'
        '{icon:m.jsx(If,{size:14,className:"text-cyan-400"}),label:"时间",value:n.timestamp,color:"text-cyan-300",outOfRange:!1}]'
    )
    new_ute_full = (
        'Q=l1(f,p),Z=(Q==null?void 0:Q.recordType)||"product",'
        'u=[{key:"temperature",icon:m.jsx(Zo,{size:14,className:"text-orange-400"}),label:"温度",value:`${n.temperature} °C`,color:"text-orange-300",outOfRange:y("temperature",n.temperature)},'
        '{key:"weight",icon:m.jsx(Jo,{size:14,className:"text-yellow-400"}),label:"重量",value:`${n.weight} g`,color:"text-yellow-300",outOfRange:y("weight",n.weight)},'
        "...(s?[{key:\"length\",icon:m.jsx($f,{size:14,className:\"text-blue-400\"}),label:\"直径\",value:`${n.length} mm`,color:\"text-blue-300\",outOfRange:y(\"length\",n.length)}]:"
        '[{key:"length",icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"长度",value:`${n.length} mm`,color:"text-blue-300",outOfRange:y("length",n.length)},'
        '{key:"width",icon:m.jsx(Mf,{size:14,className:"text-purple-400"}),label:"宽度",value:`${n.width} mm`,color:"text-purple-300",outOfRange:y("width",n.width)}]),'
        '{key:"height",icon:m.jsx(Rf,{size:14,className:"text-emerald-400"}),label:"高度",value:`${n.height} mm`,color:"text-emerald-300",outOfRange:y("height",n.height)},'
        '...o?[{key:"waterCutWidth",icon:m.jsx(Df,{size:14,className:"text-pink-400"}),label:"水切宽度",value:`${n.waterCutWidth} mm`,color:"text-pink-300",outOfRange:y("waterCutWidth",n.waterCutWidth)}]:[],'
        '{key:null,icon:m.jsx(If,{size:14,className:"text-cyan-400"}),label:"时间",value:n.timestamp,color:"text-cyan-300",outOfRange:!1}]'
        ".filter(te=>te.key==null||VisM(f,Z,te.key))"
    )
    content = _replace_once(content, old_ute_full, new_ute_full, "Ute confirm cards")

    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    content = patch(original)
    BUNDLE.write_text(content, encoding="utf-8")
    print(f"Patched {BUNDLE}")

    html = HTML.read_text(encoding="utf-8")
    html = re.sub(
        r"/assets/index-DtkarBNC\.js(\?v=[^\"]*)?",
        "/assets/index-DtkarBNC.js?v=vismetrics3",
        html,
    )
    html = re.sub(
        r"/assets/index-B8e1qPgy\.css(\?v=[^\"]*)?",
        "/assets/index-B8e1qPgy.css?v=vismetrics3",
        html,
    )
    HTML.write_text(html, encoding="utf-8")
    print("Cache-busted index.html")


if __name__ == "__main__":
    main()

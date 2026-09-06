"""Add height percentile mode to recipe UI and capture client."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"
INDEX_HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"
CACHE_TAG = "hpercentile1"

INPUT_CLS = (
    "bg-slate-800/80 border-2 border-cyan-400/40 text-cyan-50 "
    "focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50"
)


def _replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"{label}: old snippet not found:\n{old[:160]!r}")
    n = content.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, got {n}")
    return content.replace(old, new, 1)


def _pct_editor(mode_expr: str, value_expr: str, on_change: str) -> str:
    return (
        f'{mode_expr}==="percentile"?m.jsxs("div",{{className:"space-y-1 pt-1",children:['
        'm.jsx(Ae,{className:"text-sm text-cyan-200",'
        'children:"高度百分位 (0最低 / 50中位 / 100最高)"}),'
        f'm.jsx($e,{{type:"number",step:"1",min:"0",max:"100",value:{value_expr},'
        f"onChange:{on_change},"
        f'className:"{INPUT_CLS}"}})]}}):null'
    )


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")

    if 'percentile:"计算百分位"' in content and "function DtePct(" in content:
        print("percentile already present; refreshing cache only")
    else:
        content = _replace_once(
            content,
            'const Go={peak:"计算最高点",average:"计算平均点"}',
            'const Go={peak:"计算最高点",average:"计算平均点",percentile:"计算百分位"}',
            "Go labels",
        )

        content = _replace_once(
            content,
            'heightCalcMode:"peak",lwHeightMm:0,enableBottomMeasurement:!1,bottomParams:{',
            "heightCalcMode:\"peak\",heightPercentile:50,lwHeightMm:0,"
            "enableBottomMeasurement:!1,bottomParams:{",
            "Ci product heightPercentile",
        )
        bottom_mid = 'waterCutWidth:{min:0,max:0},heightCalcMode:"peak",lwHeightMm:0}'
        if content.count(bottom_mid) != 2:
            raise RuntimeError(
                f"Ci section heightPercentile anchors: expected 2, got {content.count(bottom_mid)}"
            )
        content = content.replace(
            bottom_mid,
            'waterCutWidth:{min:0,max:0},heightCalcMode:"peak",heightPercentile:50,lwHeightMm:0}',
        )

        old_lo = (
            "function LO(e){var t,r,n,a;return e?{...Ci,...e,"
            "heightCalcMode:e.heightCalcMode||Ci.heightCalcMode,"
            "lwHeightMm:e.lwHeightMm??Ci.lwHeightMm,"
            "bottomParams:{...Ci.bottomParams,...e.bottomParams||{},"
            "heightCalcMode:((t=e.bottomParams)==null?void 0:t.heightCalcMode)||Ci.bottomParams.heightCalcMode,"
            "lwHeightMm:((n=e.bottomParams)==null?void 0:n.lwHeightMm)??Ci.bottomParams.lwHeightMm},"
            "middleParams:{...Ci.middleParams,...e.middleParams||{},"
            "heightCalcMode:((r=e.middleParams)==null?void 0:r.heightCalcMode)||Ci.middleParams.heightCalcMode,"
            "lwHeightMm:((a=e.middleParams)==null?void 0:a.lwHeightMm)??Ci.middleParams.lwHeightMm}}:Ci}"
        )
        new_lo = (
            "function LO(e){var t,r,n,a,o,l;return e?{...Ci,...e,"
            "heightCalcMode:e.heightCalcMode||Ci.heightCalcMode,"
            "heightPercentile:e.heightPercentile??Ci.heightPercentile,"
            "lwHeightMm:e.lwHeightMm??Ci.lwHeightMm,"
            "bottomParams:{...Ci.bottomParams,...e.bottomParams||{},"
            "heightCalcMode:((t=e.bottomParams)==null?void 0:t.heightCalcMode)||Ci.bottomParams.heightCalcMode,"
            "heightPercentile:((o=e.bottomParams)==null?void 0:o.heightPercentile)??Ci.bottomParams.heightPercentile,"
            "lwHeightMm:((n=e.bottomParams)==null?void 0:n.lwHeightMm)??Ci.bottomParams.lwHeightMm},"
            "middleParams:{...Ci.middleParams,...e.middleParams||{},"
            "heightCalcMode:((r=e.middleParams)==null?void 0:r.heightCalcMode)||Ci.middleParams.heightCalcMode,"
            "heightPercentile:((l=e.middleParams)==null?void 0:l.heightPercentile)??Ci.middleParams.heightPercentile,"
            "lwHeightMm:((a=e.middleParams)==null?void 0:a.lwHeightMm)??Ci.middleParams.lwHeightMm}}:Ci}"
        )
        content = _replace_once(content, old_lo, new_lo, "LO merge")

        old_dtelw = (
            "function DteLw(e,t){const r=l1(e,t);const n=(r==null?void 0:r.recordType)===\"bottom\"?"
            "e.bottomParams.lwHeightMm:(r==null?void 0:r.recordType)===\"middle\"?"
            "e.middleParams.lwHeightMm:e.lwHeightMm;const a=Number(n);return Number.isFinite(a)?a:0}"
        )
        new_dtelw = (
            old_dtelw
            + 'function DtePct(e,t){const r=l1(e,t);const n=(r==null?void 0:r.recordType)==="bottom"?'
            "e.bottomParams.heightPercentile:(r==null?void 0:r.recordType)===\"middle\"?"
            "e.middleParams.heightPercentile:e.heightPercentile;const a=Number(n);"
            "return Number.isFinite(a)?Math.min(100,Math.max(0,a)):50}"
        )
        content = _replace_once(content, old_dtelw, new_dtelw, "DtePct")

        content = _replace_once(
            content,
            'body:JSON.stringify({name:e.name,waterCut:e.waterCut,heightCalcMode:e.heightCalcMode??"peak",lwHeightMm:e.lwHeightMm??0})',
            'body:JSON.stringify({name:e.name,waterCut:e.waterCut,heightCalcMode:e.heightCalcMode??"peak",'
            "lwHeightMm:e.lwHeightMm??0,"
            '...(e.heightCalcMode==="percentile"?{heightPercentile:e.heightPercentile??50}:{})})',
            "Yte body",
        )

        content = _replace_once(
            content,
            'st=ge?Dte(ge,d):"peak",lw=ge?DteLw(ge,d):0,bt=ge?$C(ge,d):""',
            'st=ge?Dte(ge,d):"peak",lw=ge?DteLw(ge,d):0,pct=ge?DtePct(ge,d):50,bt=ge?$C(ge,d):""',
            "ot pct var",
        )
        content = _replace_once(
            content,
            "Yte({name:bt,waterCut:Ie,heightCalcMode:st,lwHeightMm:lw})",
            "Yte({name:bt,waterCut:Ie,heightCalcMode:st,lwHeightMm:lw,heightPercentile:pct})",
            "ot Yte call",
        )

        old_radios = 'children:["peak","average"].map(h=>'
        if content.count(old_radios) != 3:
            raise RuntimeError(f"radio maps: expected 3, got {content.count(old_radios)}")
        content = content.replace(
            old_radios, 'children:["peak","average","percentile"].map(h=>'
        )

        old_flex = (
            'className:"flex items-center gap-5",children:["peak","average","percentile"].map'
        )
        new_flex = (
            'className:"flex items-center gap-5 flex-wrap",'
            'children:["peak","average","percentile"].map'
        )
        if content.count(old_flex) != 3:
            raise RuntimeError(f"flex wrap: expected 3, got {content.count(old_flex)}")
        content = content.replace(old_flex, new_flex)

        # Insert percentile editors inside each height-mode space-y-2 block.
        product_old = (
            'Go[h]]},h))})]}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.lwHeightMm??0,'
        )
        product_new = (
            "Go[h]]},h))}),"
            + _pct_editor(
                "a.heightCalcMode",
                "a.heightPercentile??50",
                "h=>{const v=parseFloat(h.target.value);"
                "o({...a,heightPercentile:Number.isFinite(v)?Math.min(100,Math.max(0,Math.round(v))):50})}",
            )
            + ']}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.lwHeightMm??0,'
        )
        content = _replace_once(content, product_old, product_new, "product percentile editor")

        bottom_old = (
            'Go[h]]},h))})]})]}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.bottomParams.lwHeightMm??0,'
        )
        bottom_new = (
            "Go[h]]},h))}),"
            + _pct_editor(
                "a.bottomParams.heightCalcMode",
                "a.bottomParams.heightPercentile??50",
                "h=>{const v=parseFloat(h.target.value);"
                "o({...a,bottomParams:{...a.bottomParams,"
                "heightPercentile:Number.isFinite(v)?Math.min(100,Math.max(0,Math.round(v))):50}})}",
            )
            + ']})]}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.bottomParams.lwHeightMm??0,'
        )
        content = _replace_once(content, bottom_old, bottom_new, "bottom percentile editor")

        middle_old = (
            'Go[h]]},h))})]})]})]}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.middleParams.lwHeightMm??0,'
        )
        middle_new = (
            "Go[h]]},h))}),"
            + _pct_editor(
                "a.middleParams.heightCalcMode",
                "a.middleParams.heightPercentile??50",
                "h=>{const v=parseFloat(h.target.value);"
                "o({...a,middleParams:{...a.middleParams,"
                "heightPercentile:Number.isFinite(v)?Math.min(100,Math.max(0,Math.round(v))):50}})}",
            )
            + ']})]})]}),m.jsxs("div",{className:"space-y-1 pt-1",children:['
            'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
            'm.jsx($e,{type:"number",step:"0.1",min:"0",value:a.middleParams.lwHeightMm??0,'
        )
        content = _replace_once(content, middle_old, middle_new, "middle percentile editor")

        content = _replace_once(
            content,
            'children:Go[r.heightCalcMode||"peak"]})]})',
            'children:(r.heightCalcMode||"peak")==="percentile"?'
            '`计算百分位 (${r.heightPercentile??50})`:Go[r.heightCalcMode||"peak"]})]})',
            "view product mode",
        )
        content = _replace_once(
            content,
            'children:Go[r.bottomParams.heightCalcMode||"peak"]})]})',
            'children:(r.bottomParams.heightCalcMode||"peak")==="percentile"?'
            "`计算百分位 (${r.bottomParams.heightPercentile??50})`:"
            'Go[r.bottomParams.heightCalcMode||"peak"]})]})',
            "view bottom mode",
        )
        content = _replace_once(
            content,
            'children:Go[r.middleParams.heightCalcMode||"peak"]})]})',
            'children:(r.middleParams.heightCalcMode||"peak")==="percentile"?'
            "`计算百分位 (${r.middleParams.heightPercentile??50})`:"
            'Go[r.middleParams.heightCalcMode||"peak"]})]})',
            "view middle mode",
        )

        print("frontend patches applied")

    BUNDLE.write_text(content, encoding="utf-8")

    html = INDEX_HTML.read_text(encoding="utf-8")
    html = re.sub(
        r"/assets/index-DtkarBNC\.js(\?v=[^\"]*)?",
        f"/assets/index-DtkarBNC.js?v={CACHE_TAG}",
        html,
    )
    html = re.sub(
        r"/assets/index-B8e1qPgy\.css(\?v=[^\"]*)?",
        f"/assets/index-B8e1qPgy.css?v={CACHE_TAG}",
        html,
    )
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"cache bust -> {CACHE_TAG}")

    r = subprocess.run(["node", "--check", str(BUNDLE)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"syntax error:\n{r.stderr[:500]!r}")
    print("node --check ok")


if __name__ == "__main__":
    main()

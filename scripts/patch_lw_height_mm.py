"""Add lwHeightMm (LxW working height) to recipe config and capture requests."""

from __future__ import annotations

import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"
HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"

INPUT_CLS = (
    "bg-slate-800/80 border-2 border-cyan-400/40 text-cyan-50 "
    "placeholder:text-cyan-300/50 hover:border-cyan-400/70 "
    "focus:border-cyan-400 transition-all"
)

PRODUCT_LW_FIELD = (
    'm.jsxs("div",{className:"space-y-1 pt-1",children:['
    'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
    f'm.jsx($e,{{type:"number",step:"0.1",min:"0",value:a.lwHeightMm??0,'
    f'onChange:h=>o({{...a,lwHeightMm:parseFloat(h.target.value)||0}}),'
    f'className:"{INPUT_CLS}"}})]}}),'
)

BOTTOM_LW_FIELD = (
    'm.jsxs("div",{className:"space-y-1 pt-1",children:['
    'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
    f'm.jsx($e,{{type:"number",step:"0.1",min:"0",value:a.bottomParams.lwHeightMm??0,'
    "onChange:h=>o({...a,bottomParams:{...a.bottomParams,"
    "lwHeightMm:parseFloat(h.target.value)||0}}),"
    f'className:"{INPUT_CLS}"}})]}}),'
)

MIDDLE_LW_FIELD = (
    'm.jsxs("div",{className:"space-y-1 pt-1",children:['
    'm.jsx(Ae,{className:"text-sm text-cyan-200",children:"lw校准高度(mm)"}),'
    f'm.jsx($e,{{type:"number",step:"0.1",min:"0",value:a.middleParams.lwHeightMm??0,'
    "onChange:h=>o({...a,middleParams:{...a.middleParams,"
    "lwHeightMm:parseFloat(h.target.value)||0}}),"
    f'className:"{INPUT_CLS}"}})]}}),'
)


def _replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, got {count}")
    return content.replace(old, new)


def patch(content: str) -> str:
    # Defaults in Ci
    content = _replace_once(
        content,
        'heightCalcMode:"peak",enableBottomMeasurement:!1,bottomParams:{',
        'heightCalcMode:"peak",lwHeightMm:0,enableBottomMeasurement:!1,bottomParams:{',
        "product default lwHeightMm",
    )
    content = _replace_once(
        content,
        'waterCutWidth:{min:0,max:0},heightCalcMode:"peak"},enableMiddleMeasurement:!1,middleParams:{',
        'waterCutWidth:{min:0,max:0},heightCalcMode:"peak",lwHeightMm:0},enableMiddleMeasurement:!1,middleParams:{',
        "bottom default lwHeightMm",
    )
    content = _replace_once(
        content,
        'waterCutWidth:{min:0,max:0},heightCalcMode:"peak"}};function LO(e)',
        'waterCutWidth:{min:0,max:0},heightCalcMode:"peak",lwHeightMm:0}};function LO(e)',
        "middle default lwHeightMm",
    )

    # LO normalize
    old_lo = (
        "function LO(e){var t,r;return e?{...Ci,...e,heightCalcMode:e.heightCalcMode||Ci.heightCalcMode,"
        "bottomParams:{...Ci.bottomParams,...e.bottomParams||{},heightCalcMode:((t=e.bottomParams)==null?void 0:t.heightCalcMode)||Ci.bottomParams.heightCalcMode},"
        "middleParams:{...Ci.middleParams,...e.middleParams||{},heightCalcMode:((r=e.middleParams)==null?void 0:r.heightCalcMode)||Ci.middleParams.heightCalcMode}}:Ci}"
    )
    new_lo = (
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
    content = _replace_once(content, old_lo, new_lo, "LO normalize")

    # Helper to resolve lwHeightMm by slot (after Dte)
    old_dte = (
        'function Dte(e,t){const r=l1(e,t);return(r==null?void 0:r.recordType)==="bottom"?e.bottomParams.heightCalcMode||"peak":'
        '(r==null?void 0:r.recordType)==="middle"?e.middleParams.heightCalcMode||"peak":e.heightCalcMode||"peak"}'
    )
    new_dte = old_dte + (
        "function DteLw(e,t){const r=l1(e,t);const n=(r==null?void 0:r.recordType)==="
        '"bottom"?e.bottomParams.lwHeightMm:(r==null?void 0:r.recordType)==="middle"'
        "?e.middleParams.lwHeightMm:e.lwHeightMm;const a=Number(n);return Number.isFinite(a)?a:0}"
    )
    if "function DteLw(" not in content:
        content = _replace_once(content, old_dte, new_dte, "DteLw helper")

    # Capture API client
    content = _replace_once(
        content,
        'body:JSON.stringify({name:e.name,waterCut:e.waterCut,heightCalcMode:e.heightCalcMode??"peak"})',
        'body:JSON.stringify({name:e.name,waterCut:e.waterCut,heightCalcMode:e.heightCalcMode??"peak",lwHeightMm:e.lwHeightMm??0})',
        "capture API body",
    )

    # Capture invocation
    content = _replace_once(
        content,
        'const ge=se[c],Ie=ge?DC(ge,d):!1,st=ge?Dte(ge,d):"peak",bt=ge?$C(ge,d):"";if(bt){$(!0);try{const Ke=await Yte({name:bt,waterCut:Ie,heightCalcMode:st})',
        'const ge=se[c],Ie=ge?DC(ge,d):!1,st=ge?Dte(ge,d):"peak",lw=ge?DteLw(ge,d):0,bt=ge?$C(ge,d):"";if(bt){$(!0);try{const Ke=await Yte({name:bt,waterCut:Ie,heightCalcMode:st,lwHeightMm:lw})',
        "capture invoke",
    )

    # Product form field (before enableWaterCut checkbox block that follows product height mode)
    product_anchor = (
        'name:"productHeightCalcMode",checked:a.heightCalcMode===h,onChange:()=>o({...a,heightCalcMode:h}),'
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]}),'
        'm.jsxs("div",{className:"flex items-center space-x-2 pt-2",children:[m.jsx("input",{type:"checkbox",id:"enableWaterCut"'
    )
    product_repl = (
        'name:"productHeightCalcMode",checked:a.heightCalcMode===h,onChange:()=>o({...a,heightCalcMode:h}),'
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]}),'
        + PRODUCT_LW_FIELD
        + 'm.jsxs("div",{className:"flex items-center space-x-2 pt-2",children:[m.jsx("input",{type:"checkbox",id:"enableWaterCut"'
    )
    if "children:\"lw校准高度(mm)\"" not in content.split("enableWaterCut")[0]:
        content = _replace_once(content, product_anchor, product_repl, "product form field")

    # Bottom form field
    bottom_anchor = (
        'name:"bottomHeightCalcMode",checked:a.bottomParams.heightCalcMode===h,'
        "onChange:()=>o({...a,bottomParams:{...a.bottomParams,heightCalcMode:h}}),"
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]})]}),'
        'm.jsxs("div",{className:"flex items-center space-x-2 pt-2",children:[m.jsx("input",{type:"checkbox",id:"enableMiddleMeasurement"'
    )
    bottom_repl = (
        'name:"bottomHeightCalcMode",checked:a.bottomParams.heightCalcMode===h,'
        "onChange:()=>o({...a,bottomParams:{...a.bottomParams,heightCalcMode:h}}),"
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]})]}),'
        + BOTTOM_LW_FIELD
        + 'm.jsxs("div",{className:"flex items-center space-x-2 pt-2",children:[m.jsx("input",{type:"checkbox",id:"enableMiddleMeasurement"'
    )
    content = _replace_once(content, bottom_anchor, bottom_repl, "bottom form field")

    # Middle form field (before dialog footer)
    middle_anchor = (
        'name:"middleHeightCalcMode",checked:a.middleParams.heightCalcMode===h,'
        "onChange:()=>o({...a,middleParams:{...a.middleParams,heightCalcMode:h}}),"
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]})]})]}),'
        "m.jsxs(Kd,{children:["
    )
    middle_repl = (
        'name:"middleHeightCalcMode",checked:a.middleParams.heightCalcMode===h,'
        "onChange:()=>o({...a,middleParams:{...a.middleParams,heightCalcMode:h}}),"
        'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 focus:ring-cyan-500"}),Go[h]]},h))})]})]})]}),'
        + MIDDLE_LW_FIELD
        + "m.jsxs(Kd,{children:["
    )
    content = _replace_once(content, middle_anchor, middle_repl, "middle form field")

    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    if "function DteLw(" in original and "lwHeightMm:e.lwHeightMm??0" in original:
        print("Bundle already patched; skipping JS changes")
        content = original
    else:
        content = patch(original)
        BUNDLE.write_text(content, encoding="utf-8")
        print(f"Patched {BUNDLE}")

    html = HTML.read_text(encoding="utf-8")
    html = re.sub(
        r"/assets/index-DtkarBNC\.js(\?v=[^\"]*)?",
        "/assets/index-DtkarBNC.js?v=lwheight1",
        html,
    )
    html = re.sub(
        r"/assets/index-B8e1qPgy\.css(\?v=[^\"]*)?",
        "/assets/index-B8e1qPgy.css?v=lwheight1",
        html,
    )
    HTML.write_text(html, encoding="utf-8")
    print("Cache-busted index.html")


if __name__ == "__main__":
    main()

"""Restore round-bread recipe config and diameter UI in the frontend bundle."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"

BO_HELPERS_OLD = (
    'const l=(h,p,y)=>{o({...a,[h]:{...a[h],[p]:parseFloat(y)||0}})},'
    'c=(h,p,y)=>{o({...a,bottomParams:{...a.bottomParams,[h]:{...a.bottomParams[h],[p]:parseFloat(y)||0}}})},'
    'u=(h,p,y)=>{o({...a,middleParams:{...a.middleParams,[h]:{...a.middleParams[h],[p]:parseFloat(y)||0}}})},'
    'd=()=>{r(a),t()};'
)

BO_HELPERS_NEW = (
    'const l=(h,p,y)=>{const x=parseFloat(y)||0;o(v=>{const w={...v,[h]:{...v[h],[p]:x}};'
    'return v.enableRoundBread&&h==="length"?{...w,width:{...w.width,[p]:x}}:w})},'
    'c=(h,p,y)=>{const x=parseFloat(y)||0;o(v=>{const bp={...v.bottomParams,[h]:{...v.bottomParams[h],[p]:x}},w={...v,bottomParams:bp};'
    'return v.enableRoundBread&&h==="length"?{...w,bottomParams:{...bp,width:{...bp.width,[p]:x}}}:w})},'
    'u=(h,p,y)=>{const x=parseFloat(y)||0;o(v=>{const mp={...v.middleParams,[h]:{...v.middleParams[h],[p]:x}},w={...v,middleParams:mp};'
    'return v.enableRoundBread&&h==="length"?{...w,middleParams:{...mp,width:{...mp.width,[p]:x}}}:w})},'
    'd=()=>{const h=a.enableRoundBread?{...a,width:{min:a.length.min,max:a.length.max},'
    'bottomParams:{...a.bottomParams,width:{min:a.bottomParams.length.min,max:a.bottomParams.length.max}},'
    'middleParams:{...a.middleParams,width:{min:a.middleParams.length.min,max:a.middleParams.length.max}}}:a;'
    'r(h),t()};'
)

ROUND_BREAD_CHECKBOX = (
    'm.jsxs("div",{className:"flex items-center space-x-2 pt-2",children:['
    'm.jsx("input",{type:"checkbox",id:"enableRoundBread",checked:a.enableRoundBread,'
    'onChange:h=>{const p=h.target.checked;o(p?{...a,enableRoundBread:!0,'
    'width:{min:a.length.min,max:a.length.max},'
    'bottomParams:{...a.bottomParams,width:{min:a.bottomParams.length.min,max:a.bottomParams.length.max}},'
    'middleParams:{...a.middleParams,width:{min:a.middleParams.length.min,max:a.middleParams.length.max}}}'
    ':{...a,enableRoundBread:!1})},'
    'className:"w-4 h-4 text-cyan-500 bg-slate-800 border-cyan-400/40 rounded focus:ring-cyan-500"}),'
    'm.jsx(Ae,{htmlFor:"enableRoundBread",className:"text-sm font-medium cursor-pointer text-cyan-200",children:"是否为圆包"})]}),'
)

WATERCUT_CHECKBOX_TAIL = (
    'className:"text-sm font-medium cursor-pointer text-cyan-200",children:"启用水切计算"})]}),'
)


def _diameter_grid(*, min_label: str, max_label: str, value_prefix: str, on_change: str) -> str:
    return (
        f'm.jsxs("div",{{className:"grid grid-cols-2 gap-3",children:['
        f'm.jsxs("div",{{className:"space-y-1",children:['
        f'm.jsx(Ae,{{className:"text-sm text-cyan-200",children:"{min_label}"}}),'
        f'm.jsx($e,{{type:"number",value:{value_prefix}.min,onChange:h=>{on_change}("length","min",h.target.value),'
        'className:"bg-slate-800/80 border-2 border-cyan-400/40 text-cyan-50 placeholder:text-cyan-300/50 hover:border-cyan-400/70 focus:border-cyan-400 transition-all"})]}),'
        f'm.jsxs("div",{{className:"space-y-1",children:['
        f'm.jsx(Ae,{{className:"text-sm text-cyan-200",children:"{max_label}"}}),'
        f'm.jsx($e,{{type:"number",value:{value_prefix}.max,onChange:h=>{on_change}("length","max",h.target.value),'
        'className:"bg-slate-800/80 border-2 border-cyan-400/40 text-cyan-50 placeholder:text-cyan-300/50 hover:border-cyan-400/70 focus:border-cyan-400 transition-all"})]})]})'
    )


def _wrap_lw_conditional(bo: str, *, length_marker: str, width_marker: str, height_marker: str, value_prefix: str, on_change: str, min_label: str, max_label: str) -> str:
    length_start = bo.find(length_marker)
    if length_start < 0:
        raise RuntimeError(f"Length marker not found: {length_marker}")
    grid_start = bo.rfind('m.jsxs("div",{className:"grid grid-cols-2 gap-3"', 0, length_start)
    height_marker_pos = bo.find(height_marker, length_start)
    if grid_start < 0 or height_marker_pos < 0:
        raise RuntimeError(f"Could not locate LW block for {length_marker}")
    height_grid_start = bo.rfind(
        'm.jsxs("div",{className:"grid grid-cols-2 gap-3"',
        length_start,
        height_marker_pos,
    )
    if height_grid_start < 0:
        raise RuntimeError(f"Could not locate height grid for {length_marker}")
    height_start = height_grid_start
    lw_block = bo[grid_start:height_start]
    comma = lw_block.endswith(",")
    if comma:
        lw_block = lw_block[:-1]
    diameter = _diameter_grid(
        min_label=min_label,
        max_label=max_label,
        value_prefix=value_prefix,
        on_change=on_change,
    )
    replacement = f"...(a.enableRoundBread?[{diameter}]:[{lw_block}])"
    if comma:
        replacement += ","
    return bo[:grid_start] + replacement + bo[height_start:]


def _patch_bo(content: str) -> str:
    bo_start = content.find("function BO(")
    bo_end = content.find("function Jz(", bo_start)
    if bo_start < 0 or bo_end < 0:
        raise RuntimeError("BO function not found")

    bo = content[bo_start:bo_end]
    if "是否为圆包" in bo:
        return content

    if BO_HELPERS_OLD not in bo:
        raise RuntimeError("BO helpers block not found")
    bo = bo.replace(BO_HELPERS_OLD, BO_HELPERS_NEW, 1)

    if WATERCUT_CHECKBOX_TAIL not in bo:
        raise RuntimeError("enableWaterCut checkbox block not found")
    bo = bo.replace(WATERCUT_CHECKBOX_TAIL, WATERCUT_CHECKBOX_TAIL + ROUND_BREAD_CHECKBOX, 1)

    bo = _wrap_lw_conditional(
        bo,
        length_marker='children:"长度下限 (mm)"',
        width_marker='children:"宽度下限 (mm)"',
        height_marker='children:"高度下限 (mm)"',
        value_prefix="a.length",
        on_change="l",
        min_label="直径下限 (mm)",
        max_label="直径上限 (mm)",
    )
    bo = _wrap_lw_conditional(
        bo,
        length_marker='children:"底片长度下限 (mm)"',
        width_marker='children:"底片宽度下限 (mm)"',
        height_marker='children:"底片高度下限 (mm)"',
        value_prefix="a.bottomParams.length",
        on_change="c",
        min_label="底片直径下限 (mm)",
        max_label="底片直径上限 (mm)",
    )
    bo = _wrap_lw_conditional(
        bo,
        length_marker='children:"中片长度下限 (mm)"',
        width_marker='children:"中片宽度下限 (mm)"',
        height_marker='children:"中片高度下限 (mm)"',
        value_prefix="a.middleParams.length",
        on_change="u",
        min_label="中片直径下限 (mm)",
        max_label="中片直径上限 (mm)",
    )

    return content[:bo_start] + bo + content[bo_end:]


UTE_HELPERS = (
    'function UteSP(e,t){const r=l1(e,t);return r?r.recordType==="bottom"?e.bottomParams:'
    'r.recordType==="middle"?e.middleParams:e:null}'
    'function UteOOR(e,t){if(!e||t==null||t==="")return!1;const r=parseFloat(t);'
    'return Number.isNaN(r)?!1:r<e.min||r>e.max}'
)

UTE_RECORD_NAME_OLD = (
    'children:"确认录入数据"}),m.jsxs("p",{className:"text-cyan-400/70 text-xs mt-0.5 flex items-center gap-1",'
    'children:[m.jsx(Xl,{size:11}),r]})'
)
UTE_RECORD_NAME_NEW = (
    'children:"确认录入数据"}),m.jsxs("p",{className:"text-red-400 font-bold text-2xl mt-1 flex items-center gap-1.5",'
    'children:[m.jsx(Xl,{size:18,className:"text-red-400 shrink-0"}),r]})'
)

UTE_DTE_MARKER = (
    'function Dte(e,t){const r=l1(e,t);return(r==null?void 0:r.recordType)==="bottom"?'
    'e.bottomParams.heightCalcMode||"peak"'
)

UTE_HEADER_WITH_OOR = (
    'function Ute({open:e,sampleName:t,recordName:r,data:n,imagePreviewUrl:a,sampleConfig:f,recordIndex:p,'
    'isWaterCutEnabled:o,isRoundBreadEnabled:s,onConfirm:l,onRetry:c}){if(!n)return null;'
    'const v=UteSP(f,p),y=(h,w)=>v&&w!=null&&w!==""?UteOOR(v[h],w):!1,u=['
    '{icon:m.jsx(Zo,{size:14,className:"text-orange-400"}),label:"温度",value:`${n.temperature} °C`,'
    'color:"text-orange-300",outOfRange:y("temperature",n.temperature)},'
    '{icon:m.jsx(Jo,{size:14,className:"text-yellow-400"}),label:"重量",value:`${n.weight} g`,'
    'color:"text-yellow-300",outOfRange:y("weight",n.weight)},'
    '...(s?[{icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"直径",value:`${n.length} mm`,'
    'color:"text-blue-300",outOfRange:y("length",n.length)}]:'
    '[{icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"长度",value:`${n.length} mm`,'
    'color:"text-blue-300",outOfRange:y("length",n.length)},'
    '{icon:m.jsx(Mf,{size:14,className:"text-purple-400"}),label:"宽度",value:`${n.width} mm`,'
    'color:"text-purple-300",outOfRange:y("width",n.width)}]),'
    '{icon:m.jsx(Rf,{size:14,className:"text-emerald-400"}),label:"高度",value:`${n.height} mm`,'
    'color:"text-emerald-300",outOfRange:y("height",n.height)},'
    '...o?[{icon:m.jsx(Df,{size:14,className:"text-pink-400"}),label:"水切宽度",value:`${n.waterCutWidth} mm`,'
    'color:"text-pink-300",outOfRange:y("waterCutWidth",n.waterCutWidth)}]:[],'
    '{icon:m.jsx(If,{size:14,className:"text-cyan-400"}),label:"时间",value:n.timestamp,'
    'color:"text-cyan-300",outOfRange:!1}];'
)

UTE_HEADER_RB_NO_OOR = (
    'function Ute({open:e,sampleName:t,recordName:r,data:n,imagePreviewUrl:a,isWaterCutEnabled:o,'
    'isRoundBreadEnabled:s,onConfirm:l,onRetry:c}){if(!n)return null;const u=['
    '{icon:m.jsx(Zo,{size:14,className:"text-orange-400"}),label:"温度",value:`${n.temperature} °C`,'
    'color:"text-orange-300"},{icon:m.jsx(Jo,{size:14,className:"text-yellow-400"}),label:"重量",'
    'value:`${n.weight} g`,color:"text-yellow-300"},'
    '...(s?[{icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"直径",value:`${n.length} mm`,'
    'color:"text-blue-300"}]:[{icon:m.jsx($f,{size:14,className:"text-blue-400"}),label:"长度",'
    'value:`${n.length} mm`,color:"text-blue-300"},{icon:m.jsx(Mf,{size:14,className:"text-purple-400"}),'
    'label:"宽度",value:`${n.width} mm`,color:"text-purple-300"}]),'
    '{icon:m.jsx(Rf,{size:14,className:"text-emerald-400"}),label:"高度",value:`${n.height} mm`,'
    'color:"text-emerald-300"},...o?[{icon:m.jsx(Df,{size:14,className:"text-pink-400"}),label:"水切宽度",'
    'value:`${n.waterCutWidth} mm`,color:"text-pink-300"}]:[],'
    '{icon:m.jsx(If,{size:14,className:"text-cyan-400"}),label:"时间",value:n.timestamp,color:"text-cyan-300"}];'
)

UTE_HEADER_BASE = (
    'function Ute({open:e,sampleName:t,recordName:r,data:n,imagePreviewUrl:a,isWaterCutEnabled:o,onConfirm:l,onRetry:c})'
    '{if(!n)return null;const u=[{icon:m.jsx(Zo,{size:14,className:"text-orange-400"}),label:"温度",'
    'value:`${n.temperature} °C`,color:"text-orange-300"},{icon:m.jsx(Jo,{size:14,className:"text-yellow-400"}),'
    'label:"重量",value:`${n.weight} g`,color:"text-yellow-300"},{icon:m.jsx($f,{size:14,className:"text-blue-400"}),'
    'label:"长度",value:`${n.length} mm`,color:"text-blue-300"},{icon:m.jsx(Mf,{size:14,className:"text-purple-400"}),'
    'label:"宽度",value:`${n.width} mm`,color:"text-purple-300"},{icon:m.jsx(Rf,{size:14,className:"text-emerald-400"}),'
    'label:"高度",value:`${n.height} mm`,color:"text-emerald-300"},...o?[{icon:m.jsx(Df,{size:14,className:"text-pink-400"}),'
    'label:"水切宽度",value:`${n.waterCutWidth} mm`,color:"text-pink-300"}]:[],'
    '{icon:m.jsx(If,{size:14,className:"text-cyan-400"}),label:"时间",value:n.timestamp,color:"text-cyan-300"}];'
)

UTE_VALUE_SPAN_OLD = (
    'm.jsx("span",{className:`text-sm font-medium ${d.color} drop-shadow-[0_0_6px_currentColor]`,children:d.value})'
)
UTE_VALUE_SPAN_NEW = (
    'm.jsxs("span",{className:`text-sm ${d.outOfRange?"font-bold":"font-medium"} ${d.color} '
    'drop-shadow-[0_0_6px_currentColor]`,children:[d.value,d.outOfRange?" (超出范围)":null]})'
)
UTE_VALUE_SPAN_OOR_OLD = (
    'm.jsxs("span",{className:`text-sm ${d.outOfRange?"font-bold":"font-medium"} ${d.color} '
    'drop-shadow-[0_0_6px_currentColor]`,children:[d.value,d.outOfRange?m.jsx("span",{className:"ml-2 text-xs font-bold",'
    'children:"超出范围"}):null]})'
)

KANBAN_WC_INC_HEADER_OLD = (
    '{icon:m.jsx(Rf,{size:11,className:"text-emerald-400"}),label:"高 (mm)",cls:"flex-1"},'
    '{icon:m.jsx(Df,{size:11,className:"text-pink-400"}),label:"水切 (mm)",cls:"flex-1"},'
    '{icon:m.jsx(If,{size:11,className:"text-cyan-300"}),label:"时间",cls:"flex-[1.5]"}].map(({icon:k,label:R,cls:q})'
)
KANBAN_WC_INC_HEADER_NEW = (
    '{icon:m.jsx(Rf,{size:11,className:"text-emerald-400"}),label:"高 (mm)",cls:"flex-1"},'
    '...(e?[{icon:m.jsx(Df,{size:11,className:"text-pink-400"}),label:"水切 (mm)",cls:"flex-1"}]:[]),'
    '{icon:m.jsx(If,{size:11,className:"text-cyan-300"}),label:"时间",cls:"flex-[1.5]"}].map(({icon:k,label:R,cls:q})'
)
KANBAN_WC_INC_ROW_OLD = (
    'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.height||"-"}),'
    'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:e&&k.type==="product"&&k.waterCutWidth||"-"}),'
    'm.jsx("div",{className:"flex-[1.5] px-2 text-cyan-300 text-xs",children:k.timestamp||"-"})]},k.id)})})]}):'
)
KANBAN_WC_INC_ROW_NEW = (
    'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.height||"-"}),'
    '...(e?[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),'
    'm.jsx("div",{className:"flex-[1.5] px-2 text-cyan-300 text-xs",children:k.timestamp||"-"})]},k.id)})})]}):'
)
KANBAN_WC_FULL_HEADER_OLD = (
    'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(Rf,{size:12,className:"text-emerald-400"}),"高 (mm)"]})}),'
    'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(Df,{size:12,className:"text-pink-400"}),"水切宽度 (mm)"]})}),'
    'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(If,{size:12,className:"text-cyan-300"}),"时间"]})})]})}),m.jsxs(mM,{children:[P.map(k=>'
)
KANBAN_WC_FULL_HEADER_NEW = (
    'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(Rf,{size:12,className:"text-emerald-400"}),"高 (mm)"]})}),'
    '...(e?[m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(Df,{size:12,className:"text-pink-400"}),"水切宽度 (mm)"]})})]:[]),'
    'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",'
    'children:[m.jsx(If,{size:12,className:"text-cyan-300"}),"时间"]})})]})}),m.jsxs(mM,{children:[P.map(k=>'
)
KANBAN_WC_FULL_ROW_OLD = (
    'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.height||"-"}),'
    'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:e&&k.type==="product"&&k.waterCutWidth||"-"}),'
    'm.jsx(Ft,{className:"text-cyan-300 text-xs py-2",children:k.timestamp||"-"})]},k.id)}),P.length===0&&m.jsx(Di,{children:m.jsx(Ft,{colSpan:8,'
)
KANBAN_WC_FULL_ROW_NEW = (
    'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.height||"-"}),'
    '...(e?[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),'
    'm.jsx(Ft,{className:"text-cyan-300 text-xs py-2",children:k.timestamp||"-"})]},k.id)}),P.length===0&&m.jsx(Di,{children:m.jsx(Ft,{colSpan:6+(n!=null&&n.enableRoundBread?0:1)+(e?1:0),'
)

UTE_CALL_WITH_RB = (
    'imagePreviewUrl:X==null?void 0:X.imagePreviewUrl,isWaterCutEnabled:X&&se[c]?DC(se[c],X.index):!1,'
    'isRoundBreadEnabled:X&&se[c]?RBr(se[c],X.index):!1,onConfirm:Gn,onRetry:Xn'
)
UTE_CALL_WITH_RB_OOR = (
    'imagePreviewUrl:X==null?void 0:X.imagePreviewUrl,sampleConfig:se[c],recordIndex:X==null?void 0:X.index,'
    'isWaterCutEnabled:X&&se[c]?DC(se[c],X.index):!1,isRoundBreadEnabled:X&&se[c]?RBr(se[c],X.index):!1,'
    'onConfirm:Gn,onRetry:Xn'
)


AUTH_NW_OLD = (
    'function nw(){const e=sessionStorage.getItem(rw),t=sessionStorage.getItem(tp);'
    'return!e||!t?null:Date.now()>=Number(t)?(cb(),null):e}'
)
AUTH_NW_NEW = 'function nw(){return sessionStorage.getItem(rw)}'

AUTH_EXPIRY_RELOAD = (
    'E.useEffect(()=>{Ez()&&t(!0)},[]),'
    'E.useEffect(()=>{if(e)return Cz(()=>{cb(),window.location.reload()})},[e]);'
)
AUTH_EXPIRY_RELOAD_NEW = 'E.useEffect(()=>{Ez()&&t(!0)},[]);'


def _patch_auth_no_expiry(content: str) -> str:
    if AUTH_NW_NEW in content and AUTH_EXPIRY_RELOAD not in content and AUTH_EXPIRY_RELOAD_NEW in content:
        return content

    if AUTH_NW_OLD in content:
        content = content.replace(AUTH_NW_OLD, AUTH_NW_NEW, 1)
    elif AUTH_NW_NEW not in content:
        raise RuntimeError("Auth nw() marker not found")

    if AUTH_EXPIRY_RELOAD in content:
        content = content.replace(AUTH_EXPIRY_RELOAD, AUTH_EXPIRY_RELOAD_NEW, 1)
    elif 'Cz(()=>{cb(),window.location.reload()})' in content:
        raise RuntimeError("Broken auth expiry reload marker after partial patch")

    return content


def _patch_ute_oor_format(content: str) -> str:
    if UTE_VALUE_SPAN_NEW in content:
        return content
    if UTE_VALUE_SPAN_OOR_OLD in content:
        return content.replace(UTE_VALUE_SPAN_OOR_OLD, UTE_VALUE_SPAN_NEW, 1)
    if UTE_VALUE_SPAN_OLD in content:
        return content
    raise RuntimeError("Ute out-of-range value span marker not found for format patch")


def _patch_kanban_water_cut(content: str) -> str:
    if '...(e?[{icon:m.jsx(Df,{size:11,className:"text-pink-400"}),label:"水切 (mm)"' in content:
        return content

    for old, new in (
        (KANBAN_WC_INC_HEADER_OLD, KANBAN_WC_INC_HEADER_NEW),
        (KANBAN_WC_INC_ROW_OLD, KANBAN_WC_INC_ROW_NEW),
        (KANBAN_WC_FULL_HEADER_OLD, KANBAN_WC_FULL_HEADER_NEW),
        (KANBAN_WC_FULL_ROW_OLD, KANBAN_WC_FULL_ROW_NEW),
    ):
        if new in content:
            continue
        if old not in content:
            raise RuntimeError(f"Kanban water-cut patch target not found: {old[:120]}...")
        content = content.replace(old, new, 1)
    return content


def _patch_ute_record_name_style(content: str) -> str:
    if UTE_RECORD_NAME_NEW in content:
        return content
    if UTE_RECORD_NAME_OLD not in content:
        raise RuntimeError("Ute record name header marker not found")
    return content.replace(UTE_RECORD_NAME_OLD, UTE_RECORD_NAME_NEW, 1)


def _patch_ute_out_of_range(content: str) -> str:
    if "function UteSP(" in content and UTE_VALUE_SPAN_NEW in content:
        return content

    if "function UteSP(" not in content:
        if UTE_DTE_MARKER not in content:
            raise RuntimeError("Dte marker not found for UteSP/UteOOR insert")
        content = content.replace(UTE_DTE_MARKER, UTE_HELPERS + UTE_DTE_MARKER, 1)

    if UTE_VALUE_SPAN_NEW not in content:
        if UTE_VALUE_SPAN_OLD in content:
            content = content.replace(UTE_VALUE_SPAN_OLD, UTE_VALUE_SPAN_NEW, 1)
        elif UTE_VALUE_SPAN_OOR_OLD not in content and "function UteSP(" not in content:
            raise RuntimeError("Ute value span marker not found")

    if UTE_HEADER_WITH_OOR not in content:
        for old_header in (UTE_HEADER_RB_NO_OOR, UTE_HEADER_BASE):
            if old_header in content:
                content = content.replace(old_header, UTE_HEADER_WITH_OOR, 1)
                break
        else:
            raise RuntimeError("Ute header not found for out-of-range patch")

    if UTE_CALL_WITH_RB_OOR not in content:
        if UTE_CALL_WITH_RB in content:
            content = content.replace(UTE_CALL_WITH_RB, UTE_CALL_WITH_RB_OOR, 1)
        else:
            old_call = (
                "imagePreviewUrl:X==null?void 0:X.imagePreviewUrl,isWaterCutEnabled:X&&se[c]?"
                "DC(se[c],X.index):!1,onConfirm:Gn,onRetry:Xn"
            )
            if old_call not in content:
                raise RuntimeError("Ute call site not found")
            content = content.replace(
                old_call,
                "imagePreviewUrl:X==null?void 0:X.imagePreviewUrl,sampleConfig:se[c],"
                "recordIndex:X==null?void 0:X.index,isWaterCutEnabled:X&&se[c]?"
                "DC(se[c],X.index):!1,onConfirm:Gn,onRetry:Xn",
                1,
            )

    return content


def patch(content: str) -> str:
    replacements: list[tuple[str, str]] = [
        (
            "enableWaterCut:!1,heightCalcMode:",
            "enableWaterCut:!1,enableRoundBread:!1,heightCalcMode:",
        ),
        (
            'function DC(e,t){if(!e.enableWaterCut)return!1;const r=l1(e,t);return(r==null?void 0:r.recordType)==="product"}function Dte(e,t){',
            'function RBr(e,t){return!!(e!=null&&e.enableRoundBread)}function DC(e,t){if(!e.enableWaterCut)return!1;const r=l1(e,t);return(r==null?void 0:r.recordType)==="product"}function Dte(e,t){',
        ),
        (
            "length:Ke.length,width:Ke.width,waterCutWidth:Ie?Ke.waterCutMm:\"0\",previewName:Ke.fileName",
            "length:Ke.length,width:ge&&RBr(ge,d)?Ke.length:Ke.width,waterCutWidth:Ie?Ke.waterCutMm:\"0\",previewName:Ke.fileName",
        ),
        (
            'm.jsxs("div",{className:"bg-slate-800/60 p-3 rounded-lg border border-cyan-400/20",children:[m.jsx("p",{className:"text-sm text-cyan-300",children:"长 (mm)"}),m.jsxs("p",{className:"text-cyan-50 font-medium",children:[r.length.min," ~ ",r.length.max]})]}),m.jsxs("div",{className:"bg-slate-800/60 p-3 rounded-lg border border-cyan-400/20",children:[m.jsx("p",{className:"text-sm text-cyan-300",children:"宽 (mm)"}),m.jsxs("p",{className:"text-cyan-50 font-medium",children:[r.width.min," ~ ",r.width.max]})]}),',
            '...(r.enableRoundBread?[m.jsxs("div",{className:"bg-slate-800/60 p-3 rounded-lg border border-cyan-400/20",children:[m.jsx("p",{className:"text-sm text-cyan-300",children:"直径 (mm)"}),m.jsxs("p",{className:"text-cyan-50 font-medium",children:[r.length.min," ~ ",r.length.max]})]})]:[m.jsxs("div",{className:"bg-slate-800/60 p-3 rounded-lg border border-cyan-400/20",children:[m.jsx("p",{className:"text-sm text-cyan-300",children:"长 (mm)"}),m.jsxs("p",{className:"text-cyan-50 font-medium",children:[r.length.min," ~ ",r.length.max]})]}),m.jsxs("div",{className:"bg-slate-800/60 p-3 rounded-lg border border-cyan-400/20",children:[m.jsx("p",{className:"text-sm text-cyan-300",children:"宽 (mm)"}),m.jsxs("p",{className:"text-cyan-50 font-medium",children:[r.width.min," ~ ",r.width.max]})]})]),',
        ),
        (
            'm.jsxs("div",{className:"space-y-2",children:[m.jsx("h4",{className:"font-medium text-cyan-100",children:"水切计算"}),m.jsx("p",{className:"text-cyan-200",children:r.enableWaterCut?m.jsx("span",{className:"text-emerald-400",children:"已启用"})',
            'm.jsxs("div",{className:"space-y-2",children:[m.jsx("h4",{className:"font-medium text-cyan-100",children:"圆包配置"}),m.jsx("p",{className:"text-cyan-200",children:r.enableRoundBread?m.jsx("span",{className:"text-emerald-400",children:"是圆包（录入与汇总显示直径，长宽均存直径值）"}):m.jsx("span",{className:"text-slate-400",children:"非圆包"})})]}),m.jsxs("div",{className:"space-y-2",children:[m.jsx("h4",{className:"font-medium text-cyan-100",children:"水切计算"}),m.jsx("p",{className:"text-cyan-200",children:r.enableWaterCut?m.jsx("span",{className:"text-emerald-400",children:"已启用"})',
        ),
        (
            '{icon:m.jsx($f,{size:11,className:"text-blue-400"}),label:"长 (mm)",cls:"flex-1"},{icon:m.jsx(Mf,{size:11,className:"text-purple-400"}),label:"宽 (mm)",cls:"flex-1"},{icon:m.jsx(Rf,{size:11,className:"text-emerald-400"}),label:"高 (mm)",cls:"flex-1"},{icon:m.jsx(Df,{size:11,className:"text-pink-400"}),label:"水切 (mm)",cls:"flex-1"},{icon:m.jsx(If,{size:11,className:"text-cyan-300"}),label:"时间",cls:"flex-[1.5]"}].map(({icon:k,label:R,cls:q})=>m.jsxs("div",{className:`${q} flex items-center gap-1 py-1.5 px-2`,children:[k,R]},R))}),m.jsx("div",{className:"flex-1 min-h-0 flex flex-col overflow-y-auto",children:g.length===0?',
            '...(n!=null&&n.enableRoundBread?[{icon:m.jsx($f,{size:11,className:"text-blue-400"}),label:"直径 (mm)",cls:"flex-1"}]:[{icon:m.jsx($f,{size:11,className:"text-blue-400"}),label:"长 (mm)",cls:"flex-1"},{icon:m.jsx(Mf,{size:11,className:"text-purple-400"}),label:"宽 (mm)",cls:"flex-1"}]),{icon:m.jsx(Rf,{size:11,className:"text-emerald-400"}),label:"高 (mm)",cls:"flex-1"},...(e?[{icon:m.jsx(Df,{size:11,className:"text-pink-400"}),label:"水切 (mm)",cls:"flex-1"}]:[]),{icon:m.jsx(If,{size:11,className:"text-cyan-300"}),label:"时间",cls:"flex-[1.5]"}].map(({icon:k,label:R,cls:q})=>m.jsxs("div",{className:`${q} flex items-center gap-1 py-1.5 px-2`,children:[k,R]},R))}),m.jsx("div",{className:"flex-1 min-h-0 flex flex-col overflow-y-auto",children:g.length===0?',
        ),
        (
            'm.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.length||"-"}),m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.width||"-"}),m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.height||"-"}),m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:e&&k.type==="product"&&k.waterCutWidth||"-"}),m.jsx("div",{className:"flex-[1.5] px-2 text-cyan-300 text-xs",children:k.timestamp||"-"})]},k.id)})})]}):',
            '...(n!=null&&n.enableRoundBread?[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.length||"-"})]:[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.length||"-"}),m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.width||"-"})]),m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.height||"-"}),...(e?[m.jsx("div",{className:"flex-1 px-2 text-cyan-100 text-xs",children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),m.jsx("div",{className:"flex-[1.5] px-2 text-cyan-300 text-xs",children:k.timestamp||"-"})]},k.id)})})]}):',
        ),
        (
            'm.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:12,className:"text-blue-400"}),"长 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Mf,{size:12,className:"text-purple-400"}),"宽 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Rf,{size:12,className:"text-emerald-400"}),"高 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:12,className:"text-pink-400"}),"水切宽度 (mm)"]})}),',
            '...(n!=null&&n.enableRoundBread?[m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:12,className:"text-blue-400"}),"直径 (mm)"]})})]:[m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:12,className:"text-blue-400"}),"长 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Mf,{size:12,className:"text-purple-400"}),"宽 (mm)"]})})]),m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Rf,{size:12,className:"text-emerald-400"}),"高 (mm)"]})}),...(e?[m.jsx(cr,{className:"text-cyan-300 text-xs font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:12,className:"text-pink-400"}),"水切宽度 (mm)"]})})]:[]),',
        ),
        (
            'm.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.length||"-"}),m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.width||"-"}),m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.height||"-"}),m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:e&&k.type==="product"&&k.waterCutWidth||"-"}),m.jsx(Ft,{className:"text-cyan-300 text-xs py-2",children:k.timestamp||"-"})]},k.id)}),P.length===0&&m.jsx(Di,{children:m.jsx(Ft,{colSpan:8,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})})]})]})})]})}',
            '...(n!=null&&n.enableRoundBread?[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.length||"-"})]:[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.length||"-"}),m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.width||"-"})]),m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.height||"-"}),...(e?[m.jsx(Ft,{className:"text-cyan-100 text-xs py-2",children:k.type==="product"&&k.waterCutWidth||"-"})]:[]),m.jsx(Ft,{className:"text-cyan-300 text-xs py-2",children:k.timestamp||"-"})]},k.id)}),P.length===0&&m.jsx(Di,{children:m.jsx(Ft,{colSpan:6+(n!=null&&n.enableRoundBread?0:1)+(e?1:0),className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})})]})]})})]})}',
        ),
        (
            "isWaterCutEnabled:X&&se[c]?DC(se[c],X.index):!1,onConfirm:Gn,onRetry:Xn}),m.jsx(Hte,{",
            "isWaterCutEnabled:X&&se[c]?DC(se[c],X.index):!1,isRoundBreadEnabled:X&&se[c]?RBr(se[c],X.index):!1,onConfirm:Gn,onRetry:Xn}),m.jsx(Hte,{",
        ),
        (
            'F=!!(e[d]&&e[d].enableWaterCut&&b==="product"),B=[{value:"temperature",label:"温度 (°C)"},{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},...(F?[{value:"waterCutWidth",label:"水切宽度 (mm)"}]:[])];E.useEffect(()=>{if(!d||!e[d]){r([]);return}let $=!1;async function Y(){',
            'F=!!(e[d]&&e[d].enableWaterCut&&b==="product"),_rb=!!(e[d]&&e[d].enableRoundBread);let B=[{value:"temperature",label:"温度 (°C)"},{value:"weight",label:"重量 (g)"},{value:"length",label:"长 (mm)"},{value:"width",label:"宽 (mm)"},{value:"height",label:"高 (mm)"},...(F?[{value:"waterCutWidth",label:"水切宽度 (mm)"}]:[])];_rb&&(B=B.filter($=>$.value!=="width").map($=>$.value==="length"?{value:"length",label:"直径 (mm)"}:$));E.useEffect(()=>{if(!d||!e[d]){r([]);return}let $=!1;async function Y(){',
        ),
        (
            'E.useEffect(()=>{!F&&x==="waterCutWidth"&&S("weight")},[F,x]);const V=t,K=()=>{',
            'E.useEffect(()=>{!F&&x==="waterCutWidth"&&S("weight")},[F,x]),E.useEffect(()=>{_rb||x!=="width"||S("length")},[_rb,x]);const V=t,K=()=>{',
        ),
        (
            "长:parseFloat($.length)||0,宽:parseFloat($.width)||0,高:parseFloat($.height)||0,...(F?{水切宽度:parseFloat($.waterCutWidth)||0}:{})})).reverse(),Q=$=>({temperature:\"温度\",weight:\"重量\",length:\"长\",width:\"宽\",height:\"高\",waterCutWidth:\"水切宽度\"})[$]||\"重量\",",
            "..._rb?{直径:parseFloat($.length)||0}:{长:parseFloat($.length)||0,宽:parseFloat($.width)||0},高:parseFloat($.height)||0,...(F?{水切宽度:parseFloat($.waterCutWidth)||0}:{})})).reverse(),Q=$=>_rb&&$===\"length\"?\"直径\":({temperature:\"温度\",weight:\"重量\",length:\"长\",width:\"宽\",height:\"高\",waterCutWidth:\"水切宽度\"})[$]||\"重量\",",
        ),
        (
            'm.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:13,className:"text-blue-400"}),"长 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Mf,{size:13,className:"text-purple-400"}),"宽 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Rf,{size:13,className:"text-emerald-400"}),"高 (mm)"]})}),...(F?[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:13,className:"text-pink-400"}),"水切宽度 (mm)"]})})]:[]),',
            '...(_rb?[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:13,className:"text-blue-400"}),"直径 (mm)"]})})]:[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx($f,{size:13,className:"text-blue-400"}),"长 (mm)"]})}),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Mf,{size:13,className:"text-purple-400"}),"宽 (mm)"]})})]),m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Rf,{size:13,className:"text-emerald-400"}),"高 (mm)"]})}),...(F?[m.jsx(cr,{className:"text-cyan-300 font-semibold",children:m.jsxs("span",{className:"flex items-center gap-1",children:[m.jsx(Df,{size:13,className:"text-pink-400"}),"水切宽度 (mm)"]})})]:[]),',
        ),
        (
            'm.jsx(Ft,{colSpan:F?9:8,className:"text-center text-cyan-300 py-8",children:"加载中..."})}):V.length===0?m.jsx(Di,{children:m.jsx(Ft,{colSpan:F?9:8,className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map($=>m.jsxs(Di,{className:"border-cyan-500/20 hover:bg-slate-800/40 transition-all",children:[m.jsx(Ft,{className:"text-cyan-200 font-medium",children:$.batchId||"-"}),m.jsx(Ft,{className:"text-cyan-50",children:$.sampleName}),m.jsx(Ft,{className:"text-cyan-100",children:$.temperature||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.weight||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.length||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.width||"-"}),',
            'm.jsx(Ft,{colSpan:7+(F?1:0)+(_rb?0:1),className:"text-center text-cyan-300 py-8",children:"加载中..."})}):V.length===0?m.jsx(Di,{children:m.jsx(Ft,{colSpan:7+(F?1:0)+(_rb?0:1),className:"text-center text-cyan-300 py-8",children:"暂无数据记录"})}):V.map($=>m.jsxs(Di,{className:"border-cyan-500/20 hover:bg-slate-800/40 transition-all",children:[m.jsx(Ft,{className:"text-cyan-200 font-medium",children:$.batchId||"-"}),m.jsx(Ft,{className:"text-cyan-50",children:$.sampleName}),m.jsx(Ft,{className:"text-cyan-100",children:$.temperature||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.weight||"-"}),...(_rb?[m.jsx(Ft,{className:"text-cyan-100",children:$.length||"-"})]:[m.jsx(Ft,{className:"text-cyan-100",children:$.length||"-"}),m.jsx(Ft,{className:"text-cyan-100",children:$.width||"-"})]),',
        ),
    ]

    for old, new in replacements:
        if new in content:
            continue
        if old not in content:
            raise RuntimeError(f"Patch target not found: {old[:120]}...")
        content = content.replace(old, new, 1)

    if "function RBr(" not in content:
        raise RuntimeError("RBr helper missing after patch")

    content = _patch_bo(content)
    content = _patch_ute_out_of_range(content)
    content = _patch_ute_oor_format(content)
    content = _patch_ute_record_name_style(content)
    content = _patch_kanban_water_cut(content)
    content = _patch_auth_no_expiry(content)
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

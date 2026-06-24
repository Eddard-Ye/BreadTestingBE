"""Add force-zero button and POST /api/v1/sensors/weight/zero."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

ZERO_API = (
    'async function zeroWeightSensor(){const e=await fetch("/api/v1/sensors/weight/zero",{method:"POST"});'
    'if(!e.ok)throw new mte("强制回零失败");return e.json()}'
)

OLD_API = (
    'async function tareWeightSensor(){const e=await fetch("/api/v1/sensors/weight/tare",{method:"POST"});'
    'if(!e.ok)throw new mte("重量校准失败");return e.json()}function gte()'
)
NEW_API = (
    'async function tareWeightSensor(){const e=await fetch("/api/v1/sensors/weight/tare",{method:"POST"});'
    'if(!e.ok)throw new mte("重量校准失败");return e.json()}'
    + ZERO_API
    + "function gte()"
)

OLD_O_STATE = "[M,$]=T.useState(!1),[W,F]=T.useState(null),B=async()=>{E(!0);try{await tareWeightSensor()}"
NEW_O_STATE = (
    "[M,$]=T.useState(!1),[Qe,le]=T.useState(!1),[W,F]=T.useState(null),B=async()=>{E(!0);try{await tareWeightSensor()}"
)

OLD_O_HANDLER = "finally{E(!1)}},H=async()=>{$(!0);try{await calibrateHeightSensor()}"
NEW_O_HANDLER = (
    'finally{E(!1)}},ft=async()=>{le(!0);try{await zeroWeightSensor()}catch(X){alert(X instanceof mte?X.message:"强制回零失败")}finally{le(!1)}},'
    "H=async()=>{$(!0);try{await calibrateHeightSensor()}"
)

OLD_O_BTN = (
    'children:[t.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${N?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:N?"校准中...":"就绪"})]})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs(et,{onClick:()=>A(!1),className:"flex-1 gap-2 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 shadow-lg transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs(et,{onClick:B,disabled:N,className:"flex-1 gap-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/40 hover:shadow-cyan-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),N?"校准中...":"开始校准"]})]})'
)
NEW_O_BTN = (
    'children:[t.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${N||Qe?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:N?"校准中...":Qe?"回零中...":"就绪"})]})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs(et,{onClick:()=>A(!1),className:"flex-1 gap-2 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 shadow-lg transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs(et,{onClick:B,disabled:N||Qe||!o,className:"flex-1 gap-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/40 hover:shadow-cyan-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),N?"校准中...":"开始校准"]}),m.jsxs(et,{onClick:ft,disabled:N||Qe||!o,className:"flex-1 gap-2 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 border-2 border-orange-400/50 text-white shadow-lg shadow-orange-500/40 hover:shadow-orange-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),Qe?"回零中...":"强制回零"]})]})'
)

OLD_XTE_STATE = "[O,j]=T.useState(!1),[A,C]=T.useState(!1),[P,N]=T.useState(!1),[E,M]=T.useState(null);"
NEW_XTE_STATE = (
    "[O,j]=T.useState(!1),[ze,Be]=T.useState(!1),[A,C]=T.useState(!1),[P,N]=T.useState(!1),[E,M]=T.useState(null);"
)

OLD_XTE_HOOK = "return T.useEffect(()=>{let Ce=!1;const qe=async()=>{if(Ce)return;const Sn=async(rr,Tr,Mr)=>{try{const kr=await rr();Ce||Tr(kr)}catch(kr){console.error(kr),Ce||Mr()}};await Promise.all([Sn(vte,rr=>{a(Tr=>({...Tr,temperature:rr.value,timestamp:new Date})),he(rr.connected)},()=>he(!1)),Sn(yte,rr=>{a(Tr=>({...Tr,weight:rr.value,timestamp:new Date})),pe(rr.connected)},()=>pe(!1)),Sn(gte,rr=>{a(Tr=>({...Tr,height:rr.value,timestamp:new Date})),ue(rr.connected)},()=>ue(!1))])};"
NEW_XTE_HOOK = (
    "const Ge=async()=>{j(!0);try{await tareWeightSensor()}catch(Ce){alert(Ce instanceof mte?Ce.message:\"重量校准失败\")}finally{j(!1)}},"
    "Xe=async()=>{Be(!0);try{await zeroWeightSensor()}catch(Ce){alert(Ce instanceof mte?Ce.message:\"强制回零失败\")}finally{Be(!1)}};"
    + OLD_XTE_HOOK
)

OLD_XTE_BTN = (
    'children:[n.weight.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${O?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:O?"校准中...":"就绪"})]}),m.jsx("div",{className:"h-px bg-cyan-500/15"}),m.jsx("p",{className:"text-xs text-slate-500 leading-relaxed",children:"校准完成后，传感器将以当前状态为零点基准，重新计算后续重量数值。"})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs("button",{onClick:()=>b(!1),className:"flex-1 flex items-center justify-center gap-2 h-9 rounded-md bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 text-sm transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs("button",{onClick:()=>{j(!0),setTimeout(()=>j(!1),2e3)},disabled:O,className:"flex-1 flex items-center justify-center gap-2 h-9 rounded-md bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white text-sm shadow-lg shadow-cyan-500/40 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),O?"校准中...":"开始校准"]})]})'
)
NEW_XTE_BTN = (
    'children:[n.weight.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${O||ze?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:O?"校准中...":ze?"回零中...":"就绪"})]}),m.jsx("div",{className:"h-px bg-cyan-500/15"}),m.jsx("p",{className:"text-xs text-slate-500 leading-relaxed",children:"校准完成后，传感器将以当前状态为零点基准，重新计算后续重量数值。"})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs("button",{onClick:()=>b(!1),className:"flex-1 flex items-center justify-center gap-2 h-9 rounded-md bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 text-sm transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs("button",{onClick:Ge,disabled:O||ze||!pe,className:"flex-1 flex items-center justify-center gap-2 h-9 rounded-md bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white text-sm shadow-lg shadow-cyan-500/40 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),O?"校准中...":"开始校准"]}),m.jsxs("button",{onClick:Xe,disabled:O||ze||!pe,className:"flex-1 flex items-center justify-center gap-2 h-9 rounded-md bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 border-2 border-orange-400/50 text-white text-sm shadow-lg shadow-orange-500/40 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),ze?"回零中...":"强制回零"]})]})'
)


def _replace(content: str, old: str, new: str, label: str) -> str:
    if new in content:
        return content
    if old not in content:
        raise RuntimeError(f"{label} anchor not found")
    return content.replace(old, new, 1)


def patch(content: str) -> str:
    if "async function zeroWeightSensor()" in content and "强制回零" in content:
        return content
    content = _replace(content, OLD_API, NEW_API, "zero API")
    content = _replace(content, OLD_O_STATE, NEW_O_STATE, "_O state")
    content = _replace(content, OLD_O_HANDLER, NEW_O_HANDLER, "_O zero handler")
    content = _replace(content, OLD_O_BTN, NEW_O_BTN, "_O buttons")
    content = _replace(content, OLD_XTE_STATE, NEW_XTE_STATE, "xte state")
    content = _replace(content, OLD_XTE_HOOK, NEW_XTE_HOOK, "xte handlers")
    content = _replace(content, OLD_XTE_BTN, NEW_XTE_BTN, "xte buttons")
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

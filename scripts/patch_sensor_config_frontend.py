"""Patch compiled frontend bundle for sensor serial config API + enableMock."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

OLD_HO = Path(__file__).resolve().parent / "_ho_exact.txt"
NEW_HO = '''function Ho({open:e,onClose:t,sensorName:r,sensorKey:i,accentColor:n,initialConfig:a,onSave:o}){const x=breadSensorDefaults[i]||breadSensorDefaults.temperature,w=(M,$)=>({port:(M==null?void 0:M.port)||$.port,baudRate:String((M==null?void 0:M.baudRate)||$.baudRate),dataBits:(M==null?void 0:M.dataBits)||$.dataBits,stopBits:(M==null?void 0:M.stopBits)||$.stopBits,parity:(M==null?void 0:M.parity)||$.parity,enableMock:(M==null?void 0:M.enableMock)===!1?"否":"是"}),[l,c]=T.useState(()=>w(a,x)),u=d6[n],d=[{key:"port",label:"串口号",options:o6},{key:"baudRate",label:"波特率",options:s6},{key:"dataBits",label:"数据位",options:l6},{key:"stopBits",label:"停止位",options:c6},{key:"parity",label:"校验位",options:u6,display:M=>f6[M]||M},{key:"enableMock",label:"启用Mock",options:breadMockOptions}];T.useEffect(()=>{if(!e||!i)return;let M=!1;(async()=>{try{const $=await loadSensorConfig(),W=w($[i],x);M||c(W)}catch{M||c(w(a,x))}})();return()=>{M=!0}},[e,i,a,x]);return m.jsx(an,{open:e,onOpenChange:M=>{M||t()},children:m.jsxs(Wr,{className:`bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-2 ${u.border} ${u.shadow} p-0 max-w-sm overflow-hidden`,children:[m.jsxs(Ur,{className:"sr-only",children:[r,"串口配置"]}),m.jsxs(Hr,{className:"sr-only",children:["配置",r,"传感器的串口连接参数"]}),m.jsx("div",{className:`absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent ${u.topLine} to-transparent`}),m.jsx("div",{className:`absolute -top-16 -right-16 w-32 h-32 ${u.glow} rounded-full blur-3xl pointer-events-none`}),m.jsxs("div",{className:"relative z-10 p-6",children:[m.jsxs("div",{className:"flex items-center gap-3 mb-5",children:[m.jsx("div",{className:`p-2 ${u.iconBg} rounded-lg border ${u.iconBorder}`,children:m.jsx(zL,{className:`w-5 h-5 ${u.icon}`})}),m.jsxs("div",{children:[m.jsxs("h2",{className:`${u.title} font-semibold text-base`,children:[r,"串口配置"]}),m.jsx("p",{className:`${u.sub} text-xs mt-0.5`,children:"配置传感器串口连接参数"})]})]}),m.jsx("div",{className:`bg-slate-950/60 rounded-lg border ${u.fieldBorder} overflow-hidden mb-5`,children:d.map((h,p)=>m.jsxs("div",{className:`flex items-center justify-between px-4 py-2.5 ${p<d.length-1?"border-b border-slate-700/40":""}`,children:[m.jsx("span",{className:`text-xs ${u.label}`,children:h.label}),m.jsx("select",{className:"w-36 h-7 text-xs bg-slate-800/80 border border-slate-600/50 text-slate-200 rounded-md px-2 focus:outline-none focus:ring-1 focus:ring-cyan-400/50 cursor-pointer",value:l[h.key],onChange:y=>c(b=>({...b,[h.key]:y.target.value})),children:[...(!h.options.includes(l[h.key])&&l[h.key]?[m.jsx("option",{value:l[h.key],children:h.display?h.display(l[h.key]):l[h.key]},`cur-${h.key}`)]:[]),...h.options.map(y=>m.jsx("option",{value:y,className:"bg-slate-800 text-slate-200",children:h.display?h.display(y):y},y))]})]},h.key))}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs(et,{onClick:t,className:"flex-1 gap-2 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 shadow-lg transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs(et,{onClick:async()=>{const h={port:l.port,baudRate:l.baudRate,dataBits:l.dataBits,stopBits:l.stopBits,parity:l.parity,enableMock:l.enableMock==="是"};if(o){o(h),t();return}if(!i){alert("传感器类型缺失，无法保存");return}try{const p=await loadSensorConfig();await saveSensorConfig({...p,[i]:h}),t()}catch(p){alert(p instanceof da?p.message:"保存串口配置失败，请先登录")}},className:`flex-1 gap-2 bg-gradient-to-r ${u.confirm} border-2 text-white shadow-lg transition-all`,children:[m.jsx(va,{className:"w-4 h-4"}),"保存"]})]})]})]})})}'''


def patch(content: str) -> str:
    old_ho = OLD_HO.read_text(encoding="utf-8").strip()
    if old_ho not in content:
        raise RuntimeError("Ho function block not found in bundle")

    replacements: list[tuple[str, str]] = [
        (
            'f6={None:"无",Odd:"奇",Even:"偶",Mark:"标记",Space:"空格"}',
            'f6={None:"无",Odd:"奇",Even:"偶",Mark:"标记",Space:"空格"},breadMockOptions=["是","否"]',
        ),
        (old_ho, NEW_HO),
        (
            'function gte(){return e1("height")}const bte=250',
            'function gte(){return e1("height")}const breadSensorDefaults={temperature:{port:"COM6",baudRate:"9600",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0},weight:{port:"COM6",baudRate:"38400",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0},height:{port:"COM6",baudRate:"115200",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0}};async function loadSensorConfig(){const e=await fetch("/api/v1/sensors/config");if(!e.ok)throw new da("加载串口配置失败");return e.json()}async function saveSensorConfig(e){const t=await fetch("/api/v1/sensors/config",{method:"PUT",headers:Jw(),body:JSON.stringify(e)});if(!t.ok)throw new da(await Lp(t));return t.json()}const bte=250',
        ),
        (
            'm.jsx(Ho,{open:W==="temperature",onClose:()=>F(null),sensorName:"温度",accentColor:"orange",onSave:()=>{}}),m.jsx(Ho,{open:W==="weight",onClose:()=>F(null),sensorName:"重量",accentColor:"cyan",onSave:()=>{}}),m.jsx(Ho,{open:W==="height",onClose:()=>F(null),sensorName:"高度",accentColor:"emerald",onSave:()=>{}})',
            'm.jsx(Ho,{open:W==="temperature",onClose:()=>F(null),sensorName:"温度",sensorKey:"temperature",accentColor:"orange"}),m.jsx(Ho,{open:W==="weight",onClose:()=>F(null),sensorName:"重量",sensorKey:"weight",accentColor:"cyan"}),m.jsx(Ho,{open:W==="height",onClose:()=>F(null),sensorName:"高度",sensorKey:"height",accentColor:"emerald"})',
        ),
        (
            'm.jsx(Ho,{open:E==="temperature",onClose:()=>M(null),sensorName:"温度",accentColor:"orange",onSave:()=>{}}),m.jsx(Ho,{open:E==="weight",onClose:()=>M(null),sensorName:"重量",accentColor:"cyan",onSave:()=>{}}),m.jsx(Ho,{open:E==="height",onClose:()=>M(null),sensorName:"高度",accentColor:"emerald",onSave:()=>{}})',
            'm.jsx(Ho,{open:E==="temperature",onClose:()=>M(null),sensorName:"温度",sensorKey:"temperature",accentColor:"orange"}),m.jsx(Ho,{open:E==="weight",onClose:()=>M(null),sensorName:"重量",sensorKey:"weight",accentColor:"cyan"}),m.jsx(Ho,{open:E==="height",onClose:()=>M(null),sensorName:"高度",sensorKey:"height",accentColor:"emerald"})',
        ),
    ]

    for old, new in replacements:
        if old not in content:
            raise RuntimeError(f"Patch target not found: {old[:80]}...")
        content = content.replace(old, new, 1)
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

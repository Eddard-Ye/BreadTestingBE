"""Replace smart calibration toggle with delta + hold seconds in frontend bundle."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"

OLD_DEFAULTS = (
    'ub={temperature:{port:"COM6",baudRate:"9600",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0,'
    'calibrationDelta:0,smartCalibrationEnabled:!1},weight:{port:"COM6",baudRate:"19200",dataBits:"8",'
    'stopBits:"1",parity:"None",enableMock:!0,calibrationDelta:0,smartCalibrationEnabled:!1}};'
)

NEW_DEFAULTS = (
    'ub={temperature:{port:"COM6",baudRate:"9600",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0,'
    'calibrationDelta:0,smartCalibrationDelta:0,smartCalibrationHoldSeconds:30},weight:{port:"COM6",'
    'baudRate:"19200",dataBits:"8",stopBits:"1",parity:"None",enableMock:!0,calibrationDelta:0,'
    'smartCalibrationDelta:0,smartCalibrationHoldSeconds:30}};'
)

OLD_MO = (
    'function MO(e,t="temperature"){const r=ub[t];return{port:(e==null?void 0:e.port)||r.port,'
    'baudRate:String((e==null?void 0:e.baudRate)||r.baudRate),dataBits:(e==null?void 0:e.dataBits)||r.dataBits,'
    'stopBits:(e==null?void 0:e.stopBits)||r.stopBits,parity:(e==null?void 0:e.parity)||r.parity,'
    'enableMock:(e==null?void 0:e.enableMock)!==!1,calibrationDelta:typeof(e==null?void 0:e.calibrationDelta)=="number"'
    '&&Number.isFinite(e.calibrationDelta)?e.calibrationDelta:0,smartCalibrationEnabled:(e==null?void 0:e.smartCalibrationEnabled)===!0}}'
)

NEW_MO = (
    'function MO(e,t="temperature"){const r=ub[t];const w=(M,$)=>typeof M=="number"&&Number.isFinite(M)?M:$;'
    'return{port:(e==null?void 0:e.port)||r.port,baudRate:String((e==null?void 0:e.baudRate)||r.baudRate),'
    'dataBits:(e==null?void 0:e.dataBits)||r.dataBits,stopBits:(e==null?void 0:e.stopBits)||r.stopBits,'
    'parity:(e==null?void 0:e.parity)||r.parity,enableMock:(e==null?void 0:e.enableMock)!==!1,'
    'calibrationDelta:w(e==null?void 0:e.calibrationDelta,0),smartCalibrationDelta:w(e==null?void 0:e.smartCalibrationDelta,'
    '(e==null?void 0:e.smartCalibrationEnabled)===!0?0.5:0),smartCalibrationHoldSeconds:w(e==null?void 0:e.smartCalibrationHoldSeconds,30)}}'
)

OLD_UI = (
    'n==="weight"&&m.jsxs("div",{className:"flex items-center justify-between px-4 py-2.5 border-t border-slate-700/40",'
    'children:[m.jsx("span",{className:`text-xs ${x.label}`,children:"智能校准"}),m.jsxs(qi,{value:o.smartCalibrationEnabled?"true":"false",'
    'onValueChange:g=>l(O=>({...O,smartCalibrationEnabled:g==="true"})),disabled:d||p,children:[m.jsx(Ui,{className:"w-36 h-7 text-xs '
    'bg-slate-800/80 border border-slate-600/50 text-slate-200 focus:ring-0",children:m.jsx(Wi,{})}),m.jsxs(Hi,{position:"popper",'
    'className:"z-[110] bg-slate-800/95 border border-slate-600/50 shadow-xl backdrop-blur-xl",children:[m.jsx(ni,{value:"true",'
    'className:"text-xs text-slate-200 focus:bg-slate-700/60 focus:text-slate-100",children:"开启"}),m.jsx(ni,{value:"false",'
    'className:"text-xs text-slate-200 focus:bg-slate-700/60 focus:text-slate-100",children:"关闭"})]})]})]}),'
)

NEW_UI = (
    'n==="weight"&&m.jsxs(m.Fragment,{children:[m.jsxs("div",{className:"flex items-center justify-between px-4 py-2.5 '
    'border-t border-slate-700/40",children:[m.jsx("span",{className:`text-xs ${x.label}`,children:"智能校准阈值 (g，0=关闭)"}),'
    'm.jsx($e,{type:"number",step:"0.1",min:"0",value:o.smartCalibrationDelta,onChange:g=>{const O=parseFloat(g.target.value);'
    'l(j=>({...j,smartCalibrationDelta:Number.isFinite(O)?Math.max(0,O):0}))},disabled:d||p,className:"w-36 h-7 text-xs '
    'bg-slate-800/80 border border-slate-600/50 text-slate-200 focus-visible:ring-0"})]}),m.jsxs("div",{className:"flex items-center '
    'justify-between px-4 py-2.5 border-t border-slate-700/40",children:[m.jsx("span",{className:`text-xs ${x.label}`,children:"维持时间 (秒)"}),'
    'm.jsx($e,{type:"number",step:"1",min:"1",value:o.smartCalibrationHoldSeconds,onChange:g=>{const O=parseFloat(g.target.value);'
    'l(j=>({...j,smartCalibrationHoldSeconds:Number.isFinite(O)&&O>0?O:30}))},disabled:d||p,className:"w-36 h-7 text-xs '
    'bg-slate-800/80 border border-slate-600/50 text-slate-200 focus-visible:ring-0"})]})]}),'
)


def patch(content: str) -> str:
    for name, old, new in [
        ("defaults", OLD_DEFAULTS, NEW_DEFAULTS),
        ("MO", OLD_MO, NEW_MO),
        ("UI", OLD_UI, NEW_UI),
    ]:
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

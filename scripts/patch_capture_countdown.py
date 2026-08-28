"""Add a 3s countdown prep dialog before capture API call."""

from __future__ import annotations

import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"
INDEX_HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"

CACHE_TAG = "capcd7"

CAP_CD_DLG = 'function CapCdDlg({open:e,seconds:t,onCancel:r}){return m.jsx(Pn,{open:e,onOpenChange:a=>{a||t!=null&&t>0&&r()},children:m.jsxs(an,{className:"bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-2 border-cyan-400/50 shadow-[0_0_60px_rgba(34,211,238,0.2)] p-0 overflow-hidden flex flex-col",style:{width:"56vw",maxWidth:"56vw",height:"56vh",maxHeight:"56vh"},onPointerDownOutside:a=>a.preventDefault(),children:[m.jsx("div",{className:"absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent"}),m.jsx("div",{className:"absolute -top-20 -right-20 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"}),m.jsx("div",{className:"absolute -bottom-20 -left-20 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"}),m.jsx(on,{className:"sr-only",children:"开始录入数据"}),m.jsx(sn,{className:"sr-only",children:"录入倒计时准备中"}),m.jsxs("div",{className:"relative z-10 p-8 flex-1 min-h-0 flex flex-col",children:[m.jsxs("div",{className:"text-center mb-5 flex-shrink-0",children:[m.jsx("h2",{className:"text-cyan-50 font-semibold text-2xl",children:t>0?"即将开始录入":"正在采集数据"}),m.jsx("p",{className:"text-cyan-400/70 text-sm mt-2",children:t>0?"请保持样品稳定，稍后自动采集":"正在连接视觉采集服务…"})]}),m.jsx("div",{className:"bg-slate-950/60 rounded-lg border border-cyan-500/20 px-4 py-8 flex-1 min-h-0 flex items-center justify-center",children:t>0?m.jsx("div",{className:"text-cyan-300 font-bold tabular-nums leading-none",style:{fontSize:"6rem"},children:String(t)}):m.jsx("p",{className:"text-cyan-300 text-2xl",children:"请稍候…"})})]})]})})}'


def _replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"{label}: old snippet not found")
    if content.count(old) != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, got {content.count(old)}")
    return content.replace(old, new, 1)


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")

    if "function CapCdDlg(" in content:
        print("CapCdDlg already present; skipping insert")
    else:
        anchor = "function Ute({open:e,sampleName:t,recordName:r,data:n,imagePreviewUrl:a,"
        if anchor not in content:
            raise RuntimeError("Ute anchor not found")
        content = content.replace(anchor, CAP_CD_DLG + anchor, 1)
        print("inserted CapCdDlg")

    old_state = ",[D,$]=E.useState(!1),[Y,ie]=E.useState(!1)"
    new_state = (
        ",[D,$]=E.useState(!1),[capN,capSet]=E.useState(null),"
        "capRef=E.useRef(!1),[Y,ie]=E.useState(!1)"
    )
    if "capSet]=E.useState" not in content:
        content = _replace_once(content, old_state, new_state, "capture countdown state")
        print("added countdown state")
    else:
        print("countdown state already present")

    old_ot = (
        'ot=async()=>{const ge=se[c],Ie=ge?DC(ge,d):!1,st=ge?Dte(ge,d):"peak",'
        'lw=ge?DteLw(ge,d):0,bt=ge?$C(ge,d):"";if(bt){$(!0);try{const Ke=await Yte('
        "{name:bt,waterCut:Ie,heightCalcMode:st,lwHeightMm:lw}),St=new Date,"
        "wr=MaskRec(ge,d,{temperature:Ke.temperature,weight:Ke.weight,height:Ke.height,"
        "length:Ke.length,width:ge&&RBr(ge,d)?Ke.length:Ke.width,"
        'waterCutWidth:Ie?Ke.waterCutMm:"0",previewName:Ke.fileName,'
        'timestamp:St.toLocaleString("zh-CN"),recordedAt:BC(St)});'
        "J({data:wr,index:d,name:bt,imagePreviewUrl:Ke.imagePreviewUrl})}"
        'catch(Ke){alert(Ke instanceof DI?Ke.message:"视觉采集失败")}finally{$(!1)}}'
    )
    new_ot = (
        'ot=async()=>{const ge=se[c],Ie=ge?DC(ge,d):!1,st=ge?Dte(ge,d):"peak",'
        'lw=ge?DteLw(ge,d):0,bt=ge?$C(ge,d):"";if(bt){capRef.current=!1,$(!0),capSet(3);'
        "try{for(let _s=3;_s>=1;_s-=1){if(capRef.current)return;capSet(_s);"
        "await new Promise(_r=>setTimeout(_r,1e3));if(capRef.current)return}"
        "if(capRef.current)return;capSet(0);const Ke=await Yte("
        "{name:bt,waterCut:Ie,heightCalcMode:st,lwHeightMm:lw}),St=new Date,"
        "wr=MaskRec(ge,d,{temperature:Ke.temperature,weight:Ke.weight,height:Ke.height,"
        "length:Ke.length,width:ge&&RBr(ge,d)?Ke.length:Ke.width,"
        'waterCutWidth:Ie?Ke.waterCutMm:"0",previewName:Ke.fileName,'
        'timestamp:St.toLocaleString("zh-CN"),recordedAt:BC(St)});'
        "if(capRef.current)return;"
        "J({data:wr,index:d,name:bt,imagePreviewUrl:Ke.imagePreviewUrl})}"
        "catch(Ke){capRef.current||alert(Ke instanceof DI?Ke.message:"
        '"视觉采集失败")}finally{capSet(null),$(!1)}}'
    )
    if "capSet(3)" in content and "for(let _s=3" in content:
        print("ot countdown already present")
    else:
        content = _replace_once(content, old_ot, new_ot, "capture ot handler")
        print("patched ot handler")

    ute_call = "m.jsx(Ute,{open:!!X,"
    prep_call = (
        'm.jsx(CapCdDlg,{open:capN!=null,seconds:capN==null?0:capN,'
        "onCancel:()=>{capRef.current=!0,capSet(null),$(!1)}}),"
        "m.jsx(Ute,{open:!!X,"
    )
    if "m.jsx(CapCdDlg," in content:
        print("CapCdDlg call already present")
    else:
        content = _replace_once(content, ute_call, prep_call, "CapCdDlg mount")
        print("mounted CapCdDlg")

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

    import subprocess

    r = subprocess.run(["node", "--check", str(BUNDLE)], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"syntax error:\n{r.stderr[:500]}")
    print("node --check ok")


if __name__ == "__main__":
    main()

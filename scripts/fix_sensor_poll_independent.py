"""Fix sensor polling: independent updates + no overlapping poll cycles."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

POLL_BODY = (
    "const qe=async()=>{if(Ce)return;const Sn=async(rr,Tr,Mr)=>{try{const kr=await rr();"
    "Ce||Tr(kr)}catch(kr){console.error(kr),Ce||Mr()}};await Promise.all(["
    "Sn(vte,rr=>{a(Tr=>({...Tr,temperature:rr.value,timestamp:new Date})),he(rr.connected)},()=>he(!1)),"
    "Sn(yte,rr=>{a(Tr=>({...Tr,weight:rr.value,timestamp:new Date})),pe(rr.connected)},()=>pe(!1)),"
    "Sn(gte,rr=>{a(Tr=>({...Tr,height:rr.value,timestamp:new Date})),ue(rr.connected)},()=>ue(!1))])};"
)

OLD_TAIL = (
    f"{POLL_BODY}qe();const ot=setInterval(()=>{{qe()}},bte);return()=>{{Ce=!0,clearInterval(ot)}}"
)

NEW_TAIL = (
    f"{POLL_BODY}(async()=>{{for(;!Ce;)await qe(),Ce||await new Promise(rr=>setTimeout(rr,bte))}})();"
    "return()=>{{Ce=!0}}"
)

OLD_ALL = (
    "const qe=async()=>{try{const[lt,pt,Mt]=await Promise.all([vte(),yte(),gte()]);"
    "if(Ce)return;a({temperature:lt.value,weight:pt.value,height:Mt.value,timestamp:new Date}),"
    "he(lt.connected),pe(pt.connected),ue(Mt.connected)}catch(lt){console.error(lt),"
    "Ce||(he(!1),pe(!1),ue(!1))}};qe();const ot=setInterval(()=>{qe()},bte);"
    "return()=>{Ce=!0,clearInterval(ot)}"
)


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")
    if NEW_TAIL in content:
        print("Sensor poll already uses sequential independent updates")
        return
    if OLD_TAIL in content:
        content = content.replace(OLD_TAIL, NEW_TAIL, 1)
    elif OLD_ALL in content:
        content = content.replace(OLD_ALL, NEW_TAIL, 1)
    else:
        raise RuntimeError("Poll block not found in bundle")
    BUNDLE.write_text(content, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

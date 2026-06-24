"""Replace Radix Select in Ho with native <select> (fixes Dialog pointer-events bug)."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

NATIVE_SELECT = (
    'm.jsx("select",{className:"w-36 h-7 text-xs bg-slate-800/80 border border-slate-600/50 '
    "text-slate-200 rounded-md px-2 focus:outline-none focus:ring-1 focus:ring-cyan-400/50 "
    'cursor-pointer",value:l[h.key],onChange:y=>c(b=>({...b,[h.key]:y.target.value})),'
    "children:[...(!h.options.includes(l[h.key])&&l[h.key]?"
    '[m.jsx("option",{value:l[h.key],children:h.display?h.display(l[h.key]):l[h.key]},`cur-${h.key}`)]:[]),'
    '...h.options.map(y=>m.jsx("option",{value:y,className:"bg-slate-800 text-slate-200",'
    "children:h.display?h.display(y):y},y))]})"
)

RADIX_SELECT = (
    "m.jsxs(zo,{modal:!1,value:l[h.key],onValueChange:y=>c(b=>({...b,[h.key]:y})),"
    'children:[m.jsx(qo,{className:"w-36 h-7 text-xs bg-slate-800/80 border border-slate-600/50 '
    'text-slate-200 focus:ring-0",children:m.jsx(Fo,{})}),m.jsx(Wo,{position:"popper",'
    'className:"z-[110] bg-slate-800/95 border border-slate-600/50 shadow-xl backdrop-blur-xl",'
    "children:h.options.map(y=>m.jsx(Uo,{value:y,className:\"text-xs text-slate-200 "
    'focus:bg-slate-700/60 focus:text-slate-100",children:h.display?h.display(y):y},y))})]})'
)


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")
    if NATIVE_SELECT in content:
        print("Ho already uses native select")
        return
    if RADIX_SELECT not in content:
        raise RuntimeError("Radix Select block not found in Ho — bundle may have changed")

    updated = content.replace(RADIX_SELECT, NATIVE_SELECT, 1)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Fixed Ho select in {BUNDLE}")

    # Keep patch script reference in sync
    ho_start = updated.find("function Ho(")
    ho_end = updated.find("const p6=", ho_start)
    ref = Path(__file__).resolve().parent / "_ho_current.txt"
    ref.write_text(updated[ho_start:ho_end], encoding="utf-8")


if __name__ == "__main__":
    main()

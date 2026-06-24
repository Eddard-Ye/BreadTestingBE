"""Fix weight zero status always showing 回零中 (used setter `le` instead of state `Qe`)."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

OLD = (
    'children:[t.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${N||le?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:N?"校准中...":le?"回零中...":"就绪"})]})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs(et,{onClick:()=>A(!1),className:"flex-1 gap-2 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 shadow-lg transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs(et,{onClick:B,disabled:N||le||!o,className:"flex-1 gap-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/40 hover:shadow-cyan-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),N?"校准中...":"开始校准"]}),m.jsxs(et,{onClick:ft,disabled:N||le||!o,className:"flex-1 gap-2 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 border-2 border-orange-400/50 text-white shadow-lg shadow-orange-500/40 hover:shadow-orange-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),le?"回零中...":"强制回零"]})]})'
)
NEW = (
    'children:[t.toFixed(1)," g"]})]}),m.jsxs("div",{className:"flex items-center justify-between text-sm",children:[m.jsx("span",{className:"text-slate-400",children:"校准状态"}),m.jsx("span",{className:`font-medium ${N||Qe?"text-yellow-400 animate-pulse":"text-emerald-400"}`,children:N?"校准中...":Qe?"回零中...":"就绪"})]})]}),m.jsxs("div",{className:"flex gap-3",children:[m.jsxs(et,{onClick:()=>A(!1),className:"flex-1 gap-2 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-slate-500/50 text-slate-200 shadow-lg transition-all",children:[m.jsx(Zo,{className:"w-4 h-4"}),"取消"]}),m.jsxs(et,{onClick:B,disabled:N||Qe||!o,className:"flex-1 gap-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 border-2 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/40 hover:shadow-cyan-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),N?"校准中...":"开始校准"]}),m.jsxs(et,{onClick:ft,disabled:N||Qe||!o,className:"flex-1 gap-2 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 border-2 border-orange-400/50 text-white shadow-lg shadow-orange-500/40 hover:shadow-orange-400/60 transition-all disabled:opacity-60",children:[m.jsx(va,{className:"w-4 h-4"}),Qe?"回零中...":"强制回零"]})]})'
)


def main() -> None:
    content = BUNDLE.read_text(encoding="utf-8")
    if NEW in content:
        print("Status bug already fixed")
        return
    if OLD not in content:
        raise RuntimeError("Buggy _O weight dialog block not found")
    BUNDLE.write_text(content.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"Fixed {BUNDLE}")


if __name__ == "__main__":
    main()

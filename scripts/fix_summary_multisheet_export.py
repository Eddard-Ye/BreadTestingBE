"""Switch data summary export to backend multi-sheet xlsx export."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-DtkarBNC.js"

OLD = (
    'X=async()=>{var $;try{const Y={recipeId:d,recordType:b,page:1,pageSize:Math.max(c,A)};'
    'P&&(T&&(Y.startTime=jf(T,"start")),R&&(Y.endTime=jf(R,"end")));const pe=(await kx(Y)).records.map('
    'se=>({batchId:se.batchId??"",sampleName:se.sampleName,temperature:se.temperature,weight:se.weight,'
    'length:se.length,width:se.width,height:se.height,waterCutWidth:se.waterCutWidth,timestamp:Uo(se.recordedAt)})),'
    'ae=[["批次号","名称","温度(°C)","重量(g)","长(mm)","宽(mm)","高(mm)",...(F?["水切宽度(mm)"]:[]),"时间"].join(","),'
    '...pe.map(se=>[se.batchId,se.sampleName,se.temperature,se.weight,se.length,se.width,se.height,'
    "...(F?[se.waterCutWidth]:[]),se.timestamp].join(\",\"))].join(`\\n`),de=new Blob([\"\\uFEFF\"+ae],"
    '{type:"text/csv;charset=utf-8;"}),ee=document.createElement("a"),le=URL.createObjectURL(de);'
    'ee.setAttribute("href",le),ee.setAttribute("download",`${(($=e[d])==null?void 0:$.name)||"数据汇总"}_'
    '${new Date().toLocaleDateString("zh-CN")}.csv`),ee.click()}catch(Y){alert(Y instanceof As?Y.message:"导出失败")}'
)

NEW = (
    "X=async()=>{var $;try{const Y=new URLSearchParams({recipeId:d});"
    'P&&(T&&Y.set("startTime",jf(T,"start")),R&&Y.set("endTime",jf(R,"end")));'
    "const pe=`/api/v1/measurements/export?${Y.toString()}`,"
    'ae=`${(($=e[d])==null?void 0:$.name)||"数据汇总"}_${new Date().toLocaleDateString("zh-CN")}.xlsx`;'
    "if(window.pywebview!=null&&window.pywebview.api!=null&&window.pywebview.api.save_export){"
    "const de=await window.pywebview.api.save_export(pe,ae);if(!de.ok){if(de.cancelled)return;"
    'throw new Error(de.message||"导出失败")}return}const ee=await fetch(pe);if(!ee.ok)throw new As(await $I(ee));'
    'const le=await ee.blob(),se=document.createElement("a"),ne=URL.createObjectURL(le);se.setAttribute("href",ne),'
    'se.setAttribute("download",ae),se.click(),URL.revokeObjectURL(ne)}catch(Y){alert(Y instanceof As?Y.message:'
    'Y instanceof Error?Y.message:"导出失败")}'
)


def patch(content: str) -> str:
    if NEW in content:
        return content
    if OLD not in content:
        raise RuntimeError("summary export patch point not found")
    return content.replace(OLD, NEW, 1)


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

"""Wire height calibration button to POST /api/v1/sensors/height/calibrate."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

OLD_API = 'function gte(){return e1("height")}const breadSensorDefaults'
NEW_API = (
    'function gte(){return e1("height")}'
    'async function calibrateHeightSensor(){const e=await fetch("/api/v1/sensors/height/calibrate",{method:"POST"});'
    'if(!e.ok)throw new mte("高度校准失败");return e.json()}'
    "const breadSensorDefaults"
)

OLD_H = "H=()=>{$(!0),setTimeout(()=>$(!1),2e3)}"
NEW_H = (
    'H=async()=>{$(!0);try{await calibrateHeightSensor()}catch(X){alert(X instanceof mte?X.message:"高度校准失败")}finally{$(!1)}}'
)


def patch(content: str) -> str:
    if NEW_API.split("const breadSensorDefaults")[0] in content and NEW_H in content:
        return content
    if "async function calibrateHeightSensor()" in content and NEW_H in content:
        return content
    if OLD_API not in content:
        raise RuntimeError("Height API insertion point not found")
    if OLD_H not in content:
        raise RuntimeError("Height calibrate handler not found")
    content = content.replace(OLD_API, NEW_API, 1)
    content = content.replace(OLD_H, NEW_H, 1)
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

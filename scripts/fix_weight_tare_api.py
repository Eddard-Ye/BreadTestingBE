"""Wire weight calibration button to POST /api/v1/sensors/weight/tare."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "assets" / "index-Sb-0d3gP.js"

OLD_API = 'function yte(){return e1("weight")}function gte()'
NEW_API = (
    'function yte(){return e1("weight")}'
    'async function tareWeightSensor(){const e=await fetch("/api/v1/sensors/weight/tare",{method:"POST"});'
    'if(!e.ok)throw new mte("重量校准失败");return e.json()}'
    "function gte()"
)

OLD_B = "B=()=>{E(!0),setTimeout(()=>E(!1),2e3)}"
NEW_B = (
    'B=async()=>{E(!0);try{await tareWeightSensor()}catch(X){alert(X instanceof mte?X.message:"重量校准失败")}finally{E(!1)}}'
)


def patch(content: str) -> str:
    if NEW_API.split("function gte()")[0] in content and NEW_B in content:
        return content
    if "async function tareWeightSensor()" in content and NEW_B in content:
        return content
    if OLD_API not in content:
        raise RuntimeError("Ste API insertion point not found")
    if OLD_B not in content:
        raise RuntimeError("Weight calibrate handler not found")
    content = content.replace(OLD_API, NEW_API, 1)
    content = content.replace(OLD_B, NEW_B, 1)
    return content


def main() -> None:
    original = BUNDLE.read_text(encoding="utf-8")
    updated = patch(original)
    BUNDLE.write_text(updated, encoding="utf-8")
    print(f"Patched {BUNDLE}")


if __name__ == "__main__":
    main()

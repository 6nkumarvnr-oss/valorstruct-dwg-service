from fastapi import FastAPI, UploadFile
import ezdxf

app = FastAPI()

@app.post("/interpret")
async def interpret_dwg(file: UploadFile):
    contents = await file.read()
    with open("temp.dwg", "wb") as f:
        f.write(contents)

    doc = ezdxf.readfile("temp.dwg")
    msp = doc.modelspace()

    parts = []
    for e in msp.query("LINE"):
        length = e.dxf.start.distance(e.dxf.end)
        parts.append({
            "type": "beam",
            "length_mm": round(length, 2),
            "section": "UNKNOWN"
        })

    return {"parts": parts}

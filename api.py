from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/", StaticFiles(directory="public"), name="public")
templates = Jinja2Templates(directory="public")


@app.post("/api/file")
async def infer(file: bytes = File(...)):
    return {"response": file}


@app.get("/")
async def home(path: str = "index.html"):
    return templates.TemplateResponse(path)
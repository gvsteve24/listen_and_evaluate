from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="public")
@app.get("/")
async def home():
    return templates.TemplateResponse("index.html")
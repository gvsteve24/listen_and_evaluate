import os
import shutil

import magic
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from db_handler import DBHandler
from inference import Inferer
from test_tool import TestTool

load_dotenv()

data_root = os.environ.get('BASE_DIR')
db_url = os.environ.get('DATABASE_URL')

app = FastAPI()
db = DBHandler(db_url)
inference = Inferer()

app.mount("/public", StaticFiles(directory="public", html=True), name="public")


@app.post("/api/file")
async def infer(file: UploadFile = File(...)):
    save_path = f"{data_root}/{file.filename}"

    # save file to server memory
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # save file path to server db
    db.save_one_path(save_path)
    test_tool = TestTool(db, inference)
    stt, result = test_tool.run_one_inference(save_path)                 # result is list including each score and corresponding answer

    return {"stt": stt, "result": result}


@app.get("/")
@app.get("/{path}")
async def home(path: str = "index.html"):
    file_path = f'public/{path}'
    mimetype = magic.from_file(file_path)
    return FileResponse(file_path, media_type=mimetype)

# if __name__ == "__main__":
#     uvicorn.run(app, host='localhost', port=8081)

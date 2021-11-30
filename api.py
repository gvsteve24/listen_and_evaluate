import os
import shutil

import magic
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from db_handler import DBHandler
from inference import Inferer
from test_tool import TestTool

load_dotenv()

data_root = os.getenv('BASE_DIR')
db_url = os.getenv('DATABASE_URL')
rds_url = os.getenv('RDS_URL')

db = DBHandler(rds_url)
inference = Inferer(db_handler=db)
test_tool = TestTool(db_handler=db, infer_tool=inference)

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/api/question")
async def get_question():
    item = db.retrieve_one_question(random=True)
    return {"question": item.text, "id": item.id}


@app.post("/api/file")
async def infer(file: UploadFile = File(...),  q_id: int = Form(...)):
    if not os.path.exists(data_root):
        os.mkdir(data_root)

    # default data root is (./data)
    save_path = f"{data_root}/{file.filename}"

    # save file to server memory
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # save file path to server db
    # if answer was transcribed before (same file path), it just uses db stt
    db.save_one_path(save_path, q_id)
    stt = test_tool.run_stt(save_path)
    db.save_one_answer(q_id=q_id, text=stt, path=save_path)
    return {"stt": stt}


@app.get("/api/score")
async def evaluate(text: str = "No utterance", q_id: int = None):
    result, to_save = test_tool.run_sentence_score(q_id=q_id, target_text=text)
    if to_save:
        db.save_score(query_answer=text, result=result)
    return {"result": result}


@app.get("/")
@app.get("/{path}")
async def home(path: str = "index.html"):
    file_path = f'public/{path}'
    mimetype = magic.from_file(file_path)
    return FileResponse(file_path, media_type=mimetype)

if __name__ == "__main__":
    uvicorn.run("api:app", host='0.0.0.0', port=8080)

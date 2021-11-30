import os
import shutil

import mimetypes
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
inference = Inferer()
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
    item = db.retrieve_one_path(save_path)
    stt = test_tool.run_stt(item.path)
    db.save_one_answer(q_id=q_id, text=stt, path=save_path)
    return {"stt": stt}


@app.get("/api/score")
async def evaluate(text: str = "No utterance", q_id: int = None):
    input_id = db.retrieve_input_from_answer(text)
    docs = db.retrieve_suggested_answers(q_id=q_id, input_id=input_id)
    if not docs:
        result = db.retrieve_score_and_best_by_input(input_id=input_id)
    else:
        embedding = db.retrieve_best_answer_vector(docs)
        result = test_tool.run_sentence_score(target_text=text, doc=docs, embedding=embedding)
    if docs:
        db.save_score(query_answer=text, result=result)
    return {"result": result}


@app.get("/")
@app.get("/{path}")
async def home(path: str = "index.html"):
    file_path = f'public/{path}'
    mimetype = mimetypes.guess_type(file_path)[0]
    return FileResponse(file_path, media_type=mimetype)

if __name__ == "__main__":
    uvicorn.run("api:app", host='0.0.0.0', port=8080)

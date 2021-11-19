import os
import shutil

import magic
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from db_handler import DBHandler
from inference import Inferer
from test_tool import TestTool

load_dotenv()

data_root = os.environ.get('BASE_DIR')
db_url = os.environ.get('DATABASE_URL')

db = DBHandler(db_url)
inference = Inferer()
test_tool = TestTool(db, inference)

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")
# app.mount("/components", StaticFiles(directory="public/components"), name="component")


@app.get("/api/question")
async def get_question():
    item = db.retrieve_one_question(random=True)
    return {"question": item.content, "id": item.id}


@app.post("/api/file")
async def infer(file: UploadFile = File(...),  q_id: int = Form(...)):
    save_path = f"{data_root}/{file.filename}"
    # save file to server memory
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # save file path to server db
    input_id = db.save_one_path(save_path, q_id)
    stt = test_tool.run_stt(save_path)  # result is list including each score and corresponding answer
    print(f"target_text: {stt}\nq_id: {q_id}")
    db.save_one_answer(q_id, stt, input_id)
    return {"stt": stt}


@app.get("/api/score/{text}")
@app.get("/api/score/{id}")
async def evaluate(target_text: str = "No utterance", q_id: str = None):
    result = test_tool.run_sentence_score(target_text=target_text, q_id=q_id)
    return {"result": result}


@app.get("/")
@app.get("/{path}")
async def home(path: str = "index.html"):
    file_path = f'public/{path}'
    mimetype = magic.from_file(file_path)
    return FileResponse(file_path, media_type=mimetype)

# if __name__ == "__main__":
#     uvicorn.run(app, host='localhost', port=8081)

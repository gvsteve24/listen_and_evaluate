import magic
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI()

app.mount("/", StaticFiles(directory="public", html=True), name="public")


@app.post("/api/file")
async def infer(file: bytes = File(...)):
    # save_path = f"{data_root}/userdata/{file.filename}"

    # with open(save_path, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)

    return {"response": file}


@app.get("/")
@app.get("/{path}")
async def home(path: str = "index.html"):
    file_path = f'public/{path}'
    mimetype = magic.from_file(file_path)
    return FileResponse(path, media_type=mimetype)

# if __name__ == "__main__":
#     uvicorn.run(app, host='0.0.0.0', port=8081)
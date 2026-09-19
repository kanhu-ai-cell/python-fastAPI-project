import re

from fastapi import APIRouter,UploadFile,File,Form,Depends,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from pydantic import BaseModel

router = APIRouter(
    prefix="/crud",
    tags=["Crud"])

todos=[]

class Todo(BaseModel):
    id:int
    title:str
    completed:bool

@router.post("/create/todo")
def create_todo(todo: Todo):
    todos.append(todo)
    return {
        "message": "created",
        "data": todos
    }


@router.get("/todo/list")
def todoList():
    return todos


@router.get("/todo/list/{todoId}")
def gettodoList(todoId: int):
    for to in todos:
        if to.id == todoId:
            return to

    return {
        "error": "Not found todoid"
    }


@router.put("/todo/update/{todoId}")
def updateTodo(todoId: int, updatedTodo: Todo):
    for index, todo in enumerate(todos):
        if todo.id == todoId:
            todos[index] = updatedTodo

            return {
                "message": "data updated",
                "data": updatedTodo
            }

    return {
        "error": "todo not found"
    }


@router.delete("/todo/delete/{todoId}")
def deleteTodo(todoId: int):
    for index, todo in enumerate(todos):
        if todo.id == todoId:
            todos.pop(index)

            return {
                "message": "data deleted"
            }

    return {
        "error": "todo not found"
    }

# her we have achieved the File uploading & serving static files
# from fastapi import UploadFile,File,Form,Depends,HTTPException
# from fastapi.staticfiles import StaticFiles
# import os
# import shutil
# Step 1: Create a directory to store uploaded files
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# setp-2: Static file set-up
# URL : http://127.0.0.1:8000/FILE/<filename>
router.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# stp-3: Create an endpoint to handle file uploads
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save the uploaded file to the UPLOAD_DIR
    fileName = re.sub(r"\s+", "_", file.filename)
    file_path = os.path.join(UPLOAD_DIR, fileName)
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
   
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": fileName,
        # "url": f"/files/{fileName}"
        "url": f"http://127.0.0.1:8000/crud/files/{fileName}"
    }

# setp-4: Get file URL api
@router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "file_url": f"http://127.0.0.1:8000/crud/files/{filename}"
    }

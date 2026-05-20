from fastapi import FastAPI, File, UploadFile
import os
import shutil
from pydantic import BaseModel

from tasks import run_llm_graph
from celery.result import AsyncResult
from celery_app import app_celery

from process_doc import load_store_doc

class ChatRequest(BaseModel):
    user_id:str
    message:str
    database_name:str

app=FastAPI()

@app.post('/chat')
async def chat(request:ChatRequest):
    task=run_llm_graph.delay(user_id=request.user_id,
    message=request.message,db_name=request.database_name)

    return {
        'task_id':task.id,
        'status':'queued'
    }

@app.get('/result/{task_id}')
def result(task_id:str):
    result=AsyncResult(id=task_id,app=app_celery)

    return{
        'result_status':result.status,
        'result':result.result
    }



@app.post('/upload')
async def upload(file:UploadFile=File(...)):
    UPLOAD_DIR='./uploads'
    os.makedirs(name=UPLOAD_DIR,exist_ok=True)

    file_path=os.path.join(UPLOAD_DIR,file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task=load_store_doc.delay(file_path=file_path,database_name=file.filename)

    return {
        'task_id':task.id,
        'status':'queued'
    }


 
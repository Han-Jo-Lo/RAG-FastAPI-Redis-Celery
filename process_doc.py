from load_doc import load_file
from vector_store import VectorStoreManager
import os
from langchain_openai.embeddings import OpenAIEmbeddings
from paths import vector_db_path
from config import get_embeddings
from celery_app import app_celery

embedding=get_embeddings()

@app_celery.task
def load_store_doc (file_path:str,database_name:str):
    path_vs=vector_db_path(database_name)

    database=VectorStoreManager(embedding_model=embedding,persist_directory=path_vs)

    if not os.path.exists(database.persist_directory):
        chunked_doc=load_file(file_path,
        embedding_model=embedding)
        database.create_or_update(chunked_doc)
        return {'message':'base de datos creada con nombre '+database_name}
    else:
        return {'message':"Base de datos ya esta creada"}
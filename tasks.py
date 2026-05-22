from config import get_embeddings,get_redis
from celery_app import app_celery
from graph import build_graph
from langchain_core.messages import HumanMessage

from vector_store import VectorStoreManager
from paths import vector_db_path
from functools import lru_cache


@lru_cache(maxsize=64)
def get_vector_store_for_db(db_name:str):
    vs=VectorStoreManager(
        embedding_model=get_embeddings(),
        persist_directory=vector_db_path(db_name)
    )
    vs.load()
    return vs



@app_celery.task
def run_llm_graph(user_id:str,message:str,db_name:str):

    config = {"configurable": {"thread_id": user_id}}

    message_to_llm=HumanMessage(content=message)

    vs=get_vector_store_for_db(db_name)
    checkpointer=get_redis()
    Graph=build_graph(vs,checkpointer)

    response=Graph.invoke({'messages':[message_to_llm]},config=config)

    last_message=response['messages'][-1].content

    return last_message
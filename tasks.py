from config import get_embeddings
from memory import save_memory,load_memory
from celery_app import app_celery
from graph import build_graph
from langchain_core.messages import HumanMessage,AIMessage

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
    history=load_memory(user_id=user_id)
    langgraph_messages=[]

    for msg in history:
        if msg['role']=='user':
            langgraph_messages.append(HumanMessage(content=msg['message']))
        elif msg['role']=='assistant':
            langgraph_messages.append(AIMessage(content=msg['message']))

    langgraph_messages.append(HumanMessage(content=message))


    vs=get_vector_store_for_db(db_name)
    
    Graph=build_graph(vs)

    response=Graph.invoke({'messages':langgraph_messages})

    updated_messages=response['messages']
    last_message=updated_messages[-1].content

    serialized_msg=[]

    for msg in updated_messages:
        if isinstance(msg,HumanMessage):
            serialized_msg.append({'role':'user','message':msg.content})
        else:
            serialized_msg.append({'role':'assistant','message':msg.content})

    save_memory(user_id=user_id,messages=serialized_msg)

    return last_message
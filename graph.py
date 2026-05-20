
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage,AIMessage
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START,END,StateGraph
from dotenv import load_dotenv

load_dotenv()

from vector_store import VectorStoreManager
from config import get_llm

llm=get_llm()

SYSTEM_INSTRUCTIONS = (
    "Eres un asistente de soporte técnico experto. Tu objetivo es ayudar "
    "a los usuarios basándote exclusivamente en el contexto proporcionado.\n"
    "REGLAS CRÍTICAS:\n"
    "1. Usa el CONTEXTO_RECUPERADO para responder.\n"
    "2. Si la respuesta no está en el contexto, di: 'Lo siento, no tengo esa información'.\n"
    "3. Responde siempre en español de forma profesional."
)

class State(TypedDict):
    messages:Annotated[list,add_messages]
    retrieve_context:str
    


def build_graph(vector_store:VectorStoreManager):
    
    def context_node(state:State):
        pregunta=state['messages'][-1].content
        context=vector_store.retrieve(pregunta)
        return {'retrieve_context':context}

    def chatbot_node(state:State):
        context=state.get('retrieve_context','No hay contexto')
        messages=state['messages']
        

        prompt_msgs=[
            SystemMessage(content=(
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"<contexto_recuperado>\n{context}\n</contexto_recuperado>"
        ))
        ]+messages
        

        response=llm.invoke(prompt_msgs)
    
        return {'messages':[response]}

    builder=StateGraph(State)
    builder.add_node('chatbot',chatbot_node)
    builder.add_node('context',context_node)
    
    builder.add_edge(START,'context')
    builder.add_edge('context','chatbot')
    builder.add_edge('chatbot',END)

    return builder.compile()




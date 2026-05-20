import os
from langchain_core.messages import SystemMessage,RemoveMessage
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
    summary:str
    no_answer:bool
    


def build_graph(vector_store:VectorStoreManager,checkpointer=None):
    
    def context_node(state:State):
        pregunta=state['messages'][-1].content
        context=vector_store.retrieve(pregunta)
        context_str = "\n\n---\n\n".join(doc.page_content for doc in context)
        return {"retrieve_context": context_str}

    def chatbot_node(state:State):
        context=state['retrieve_context']
        messages=state['messages']
        summary=state.get('summary','')
        summary_context=f'Resumen de la conversacion previa: {summary}\n' if summary else ''
        

        prompt_msgs=[
            SystemMessage(content=(
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f'{summary_context}\n'
        f"<contexto_recuperado>\n{context}\n</contexto_recuperado>"
        ))
        ]+messages
        
        response=llm.invoke(prompt_msgs)
    
        return {'messages':[response]}

    def unknown_answer(state:State):
        last_message=state['messages'][-1].content
        flag_question='Lo siento, no tengo esa información' in last_message
        return {'no_answer':flag_question}

    def summarize_memory(state: State):

        messages = state["messages"]
        summary = state.get("summary", "")

        if len(messages) < 10:
            return {}

        prompt_msgs = [SystemMessage(content=(
        f"resumen actual: {summary} \n\n"
        f'Eres un sistema que hace resumen de una conversacion utilizando\n'
        f'el resumen dado anteriormente y las conversaciones dadas a continuacion'
        ))]+messages
        
        new_summary = llm.invoke(prompt_msgs)
        

        messages_to_remove = [RemoveMessage(id=m.id) for m in messages[:-6] if m.id]

        return {
            "summary": new_summary.content,
            "messages": messages_to_remove
        }

    def should_summarize(state: State):
        if len(state["messages"]) >= 10:
            return "summarize"
        return END

    builder = StateGraph(State)
    builder.add_node("context", context_node)
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("summarize", summarize_memory)
    builder.add_node('no_answer',unknown_answer)

    builder.add_edge(START, "context")
    builder.add_edge("context", "chatbot")
    builder.add_edge("chatbot", 'no_answer')

    builder.add_conditional_edges(
        source='no_answer',
        path=should_summarize,
        path_map={
            'summarize':'summarize',
            END:END
        }
    )

    return builder.compile(checkpointer=checkpointer)





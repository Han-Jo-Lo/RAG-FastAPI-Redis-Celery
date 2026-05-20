from functools import lru_cache
import os

from dotenv import load_dotenv
load_dotenv()

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
LLM_MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)
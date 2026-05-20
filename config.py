from functools import lru_cache
import os

from dotenv import load_dotenv
load_dotenv()

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from langgraph.checkpoint.redis import RedisSaver
from redis import Redis

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
LLM_MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

@lru_cache(maxsize=1)
def get_redis()->RedisSaver:
    client = Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT')
    , db=os.getenv('REDIS_DB'))
    memory_saver=RedisSaver(redis_client=client)
    memory_saver.setup()
    return memory_saver 
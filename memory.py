import redis
import json
import os

redis_client=redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    db=os.getenv('REDIS_DB'),
    decode_responses=True
)

MAX_MESSAGES=10

def save_memory(user_id:str,messages:list):
    redis_client.set(user_id,json.dumps(messages[-MAX_MESSAGES:]))

def load_memory(user_id:str):
    data=redis_client.get(user_id)

    if data:
        return json.loads(data)

    return []
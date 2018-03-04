import asyncio
import uvloop
import socketserver
from collections import deque
from blinker import signal
from concurrent.futures import ThreadPoolExecutor
from config import REDIS_HOST, REDIS_PORT, REDIS_DB
from config import HOST, PORT
from utils import log
# from utils import rpush_redis
import redis
import time


async def service_test(data):
    print(data)
    return "success"



if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(loop.run_until_complete(handler()))



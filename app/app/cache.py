from redis.asyncio import Redis
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


class Cache:
    def __init__(self) -> None:
        self.cache = Redis(
            host=os.environ["CACHE_HOST"],
            port=int(os.environ["CACHE_PORT"]),
            decode_responses=True,
        )

    async def __aenter__(self):
        return self

    async def check(self, hash_file) -> None | str:
        pass

    async def set_task_id(self, hash_file: str, task_id: int) -> None:
        pass
    
    async def set_llm_response(self, hash_file: str, llm_response: str) -> None:
        pass

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.cache.aclose()

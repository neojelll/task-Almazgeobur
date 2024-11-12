import os
from dotenv import load_dotenv
from loguru import logger
from redis.asyncio import Redis
from .logger import configure_logger


configure_logger()


class Cache:
    def __init__(self):
        try:
            logger.debug('Start init redis session')
            load_dotenv()
            self.cache = Redis(
                host=os.environ['CACHE_HOST'],
                port=int(os.environ['CACHE_PORT']),
                decode_responses=True,
            )
            self.ttl = int(os.environ['CACHE_TTL'])
            logger.debug('Completed init redis session')
        except Exception as e:
            logger.error(f'Error when init redis session: {e}')

    async def __aenter__(self):
        return self

    async def check(self, hash_file: str) -> str | None:
        try:
            logger.debug(f'Start checking cache for: {hash_file}')
            if await self.cache.exists(hash_file):
                return await self.cache.get(hash_file)
            logger.debug('Completed check in cache')
        except Exception as e:
            logger.error(f'Error when check in cache: {e}')

    async def set_task_id(self, task_id, hash_file: str):
        try:
            logger.debug(f'Start set_task_id with params: {task_id, hash_file}')
            await self.cache.set(str(task_id), hash_file)
            logger.debug('Completed set_task_id')
        except Exception as e:
            logger.error(f'Error when set to cache: {e}')

    async def delete_task_id(self, task_id):
        try:
            logger.debug(f'Start delete task_id in cache with params: {task_id}')
            await self.cache.delete(str(task_id))
            logger.debug('Completed delete_task_id')
        except Exception as e:
            logger.error(f'Error when delete record in cache: {e}')

    async def set_llm_response(self, hash_file: str, llm_response):
        try:
            logger.debug(
                f'Start set_llm_response with params: {hash_file, llm_response}'
            )
            await self.cache.set(hash_file, llm_response, ex=self.ttl)
            logger.debug('Completed set_llm_response')
        except Exception as e:
            logger.error(f'Error when set_llm_response: {e}')

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cache.aclose()

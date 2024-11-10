from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Product, Task, LLMResponse
from sqlalchemy import select
from .logger import configure_logger
from loguru import logger
from dotenv import load_dotenv
import os


configure_logger()


class DataBase:
    def __init__(self):
        try:
            logger.debug('Start init database session')
            load_dotenv()
            database_url = f'postgresql+asyncpg://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

            self.async_engine = create_async_engine(
                database_url, echo=True, future=True
            )
            self.async_session = async_sessionmaker(
                bind=self.async_engine, class_=AsyncSession, expire_on_commit=False
            )()

            logger.debug('Completed init database session')
        except Exception as e:
            logger.error(f'Error when init database session: {e}')

    async def __aenter__(self):
        return self

    async def create_record_product(self, task_id, sales_date: str, product: dict):
        try:
            logger.debug(
                f'Start create_record_product with params: {sales_date, product}'
            )
            new_product = Product(
                task_id=task_id,
                name=product['name'],
                quantity=product['quantity'],
                price=product['price'],
                category=product['category'],
                date=sales_date,
            )

            self.async_session.add(new_product)
            await self.async_session.commit()

            logger.debug('Completed create_record_product')
        except Exception as e:
            logger.error(f'Error when create_record_product: {e}')

    async def create_record_task(self, hash_file: str):
        try:
            logger.debug(f'Start create_record_task with params: {hash_file}')
            new_task = Task(hash_file=hash_file)

            self.async_session.add(new_task)
            await self.async_session.commit()

            logger.debug('Completed create_record_task')
            return new_task.id
        except Exception as e:
            logger.error(f'Error when create_record_task: {e}')

    async def create_record_llm_response(self, task_id, response):
        try:
            logger.debug(
                f'Start create_record_llm_response with params: {task_id, response}'
            )
            new_llm_response = LLMResponse(task_id=task_id, response=response)

            self.async_session.add(new_llm_response)
            await self.async_session.commit()

            logger.debug('Completed create_record_llm_response')
        except Exception as e:
            logger.error(f'Error when create_record_llm_response: {e}')

    async def check_response(self, hash_file: str) -> str | None:
        try:
            logger.debug(f'Start check_response with params: {hash_file}')
            result = await self.async_session.execute(
                select(Task).filter(Task.hash_file == hash_file)
            )
            task = result.scalars().first()

            if task:
                return_value = task.llm_response.response
                logger.debug(f'Completed check_response returned: {return_value}')
                return return_value
            logger.debug('Completed check_response returned: None')
        except Exception as e:
            logger.error(f'Error when check_response: {e}')

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.async_session.aclose()

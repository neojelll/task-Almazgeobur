from sqlalchemy.ext.asyncio import (
	create_async_engine,
	AsyncSession,
	async_sessionmaker
)
from .models import Product, Task
from sqlalchemy import select
from .logger import configure_logger
from loguru import logger
from dotenv import load_dotenv
import os


configure_logger()


class DataBase:
	def __init__(self) -> None:
		load_dotenv()
		database_url = f'postgresql+asyncpg://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
		self.async_engine = create_async_engine(database_url, echo=True, future=True)
		self.async_session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)

	async def __aenter__(self):
		self.session = self.async_session()
		return self
	
	async def create_records_product(self, sales_date: str, products: list[dict]) -> None:
		pass

	async def create_record_task(self, status: str) -> int:
		return 1

	async def update_task_status(self, task_id: int, status: str) -> None:
		pass

	async def create_record_llm_response(self, task_id: int, response: str) -> None:
		pass
	
	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		await self.session.aclose()

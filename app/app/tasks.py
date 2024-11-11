from .llm import send_prompt_to_claude_api
from fastapi import HTTPException, status
from .parser import parse_xml
from .db import DataBase
from .logger import configure_logger
from loguru import logger
from .celery import celery
from .cache import Cache
import asyncio


configure_logger()


async def async_func(task, file_content: bytes, hash_file: str):
    logger.debug(f'Start task with params: {file_content}\n{hash_file}')
    task.update_state(state='Get XML')
    hash_file, task_id, sales_date, products = await parse_xml(file_content, hash_file)
    task.update_state(state='Processed XML')

    total_revenue = sum(product['quantity'] * product['price'] for product in products)

    top_products = sorted(products, key=lambda x: x['quantity'], reverse=True)[:3]

    categories = {}

    for product in products:
        if product['category'] not in categories:
            categories[product['category']] = 0
        categories[product['category']] += product['quantity']

    prompt = f'Проанализируй данные о продажах за {sales_date}:\n'
    prompt += f'1. Общая выручка: {total_revenue}\n'
    prompt += f"2. Топ-3 товара по продажам: {[(product['name'], product['quantity']) for product in top_products]}\n"
    prompt += f'3. Распределение по категориям: {categories}\n\n'
    prompt += 'Составь краткий аналитический отчет с выводами и рекомендациями.'

    async with DataBase() as database:
        task.update_state(state='A report is generated')

        response = await send_prompt_to_claude_api(prompt)

        if response is None:
            logger.error('response is None')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Server side error',
            )

        await database.create_record_llm_response(task_id, response)

        task.update_state(state='The report has been generated')

        async with Cache() as cache:
            await cache.delete_task_id(task_id)
            await cache.set_llm_response(hash_file, response)

        logger.debug('Completed task')


@celery.task(bind=True)
def process_sales_data(self, file_content: bytes, hash_file: str):
    asyncio.run(async_func(self, file_content, hash_file))

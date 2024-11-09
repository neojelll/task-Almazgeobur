from .llm import send_prompt_to_claude_api
from .db import DataBase
from celery import Celery


celery_app = Celery('app')


@celery_app.task
async def process_sales_data(task_id: int, sales_date: str, products: list[dict]) -> None:
	total_revenue = sum(product['quantity'] * product['price'] for product in products)

	top_products = sorted(products, key=lambda x: x['quantity'], reverse=True)[:3]

	categories = {}

	for product in products:
		if product['category'] not in categories:
			categories[product['category']] = 0
		categories[product['category']] += product['quantity']

	prompt = f"Проанализируй данные о продажах за {sales_date}:\n"
	prompt += f"1. Общая выручка: {total_revenue}\n"
	prompt += f"2. Топ-3 товара по продажам: {[(product['name'], product['quantity']) for product in top_products]}\n"
	prompt += f"3. Распределение по категориям: {categories}\n\n"
	prompt += "Составь краткий аналитический отчет с выводами и рекомендациями."

	async with DataBase() as database:
		await database.update_task_status(task_id, 'Формируется отчет')

		response: str = await send_prompt_to_claude_api(prompt)

		await database.create_record_llm_response(task_id, response)

		await database.update_task_status(task_id, 'Создан отчет')

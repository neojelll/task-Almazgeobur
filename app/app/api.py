from fastapi import FastAPI, UploadFile, File
from .logger import configure_logger
from .parser import parse_xml
from loguru import logger
from .tasks import process_sales_data


configure_logger()


app = FastAPI()


@app.post('/upload')
async def get_xml(file: UploadFile = File(...)) -> None:
	task_id, sales_date, products = await parse_xml(file)
	process_sales_data.delay(task_id, sales_date, products)

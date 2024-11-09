from fastapi import HTTPException, status
from .logger import configure_logger
from .cache import Cache
from .db import DataBase
from loguru import logger
from lxml import etree
import hashlib


configure_logger()


async def parse_xml(file) -> tuple[int, str, list[dict]]:
	try:
		logger.debug(f'Start parse_xml, params: {file}')

		if not file.filename.endswith('.xml'):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Uploaded file is not a valid XML file')
		
		if file.content_type not in ['application/xml', 'text/xml', 'application/xhtml+xml']:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Uploaded file is not a valid XML file')
		
		async with DataBase() as database:
			task_id: int = await database.create_record_task('Получен XML')

			file_content: bytes = await file.read()

			hash_object = hashlib.sha256()
			hash_object.update(file_content)
			hash_file_hex = hash_object.hexdigest()

			async with Cache() as cache:
				await cache.set_task_id(hash_file_hex, task_id)

			parser = etree.XMLParser()
			root = etree.fromstring(file_content, parser)

			sales_date: str = root.attrib['date']
			products_element = root.find('products')

			products: list[dict] = []

			if products_element is not None:
				for product in root.find('products').findall('product'):
					product_id: int = int(product.find('id').text)
					product_name: str = product.find('name').text
					product_quantity: int = int(product.find('quantity').text)
					product_price: float = float(product.find('price').text)
					product_category: str = product.find('category').text

					products.append({
						'id': product_id,
						'name': product_name,
						'quantity': product_quantity,
						'price': product_price,
						'category': product_category,
					})
			else:
				logger.warning('No products element found')

			await database.update_task_status(task_id, 'Обработан XML')

		logger.debug('Completed parse_xml')
		return task_id, sales_date, products
	
	except etree.XMLSyntaxError as e:
		logger.error(f'XML syntax error: {e}')
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='server side error')
	
	except Exception as e:
		logger.error(f'Error when parse_xml: {e}')
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='server side error')

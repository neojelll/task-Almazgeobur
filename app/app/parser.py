from fastapi import HTTPException, status
from .logger import configure_logger
from .cache import Cache
from .db import DataBase
from loguru import logger
from lxml import etree


configure_logger()


async def parse_xml(file_content: bytes, hash_file_hex: str) -> tuple:
    try:
        logger.debug(f'Start parse_xml, params: {file_content}')

        async with DataBase() as database:
            task_id = await database.create_record_task(hash_file_hex)

            if task_id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Server side error',
                )

            async with Cache() as cache:
                await cache.set_task_id(task_id, hash_file_hex)

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

                    product = {
                        'id': product_id,
                        'name': product_name,
                        'quantity': product_quantity,
                        'price': product_price,
                        'category': product_category,
                    }

                    await database.create_record_product(task_id, sales_date, product)

                    products.append(product)
            else:
                logger.warning('No products element found')

        logger.debug('Completed parse_xml')
        return hash_file_hex, task_id, sales_date, products

    except etree.XMLSyntaxError as e:
        logger.error(f'XML syntax error: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Server side error',
        )

    except Exception as e:
        logger.error(f'Error when parse_xml: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Server side error',
        )

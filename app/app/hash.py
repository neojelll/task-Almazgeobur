import hashlib
from fastapi import HTTPException, status
from loguru import logger
from .logger import configure_logger


configure_logger()


async def hashed_file(file_content: bytes) -> str:
    try:
        logger.debug(f'Start hashed_file with params: {file_content}')
        hash_object = hashlib.sha256()
        hash_object.update(file_content)
        return_value = hash_object.hexdigest()
        logger.debug(f'Completed hashed_file returned: {return_value}')
        return return_value
    except Exception as e:
        logger.error(f'Error when hashed_file: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Server side error',
        )

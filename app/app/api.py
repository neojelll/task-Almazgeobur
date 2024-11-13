from fastapi import FastAPI, UploadFile, File, HTTPException, status
from .cache import Cache
from .db import DataBase
from .hash import hashed_file
from .tasks import process_sales_data


app = FastAPI()


@app.post('/upload')
async def send_xml(file: UploadFile = File(...)) -> dict[str, str | None]:
    if not file.filename.endswith('.xml'):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Uploaded file is not a valid XML file',
        )

    if file.content_type not in [
        'application/xml',
        'text/xml',
        'application/xhtml+xml',
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Uploaded file is not a valid XML file',
        )

    file_content: bytes = await file.read()
    hash_file = await hashed_file(file_content)

    async with DataBase() as database:
        result = await database.check_response(hash_file)

        if result is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You are trying to send a file that you sent before',
            )

    process_sales_data.delay(file_content, hash_file)
    return {'hash_file': hash_file}


@app.get('/report')
async def get_report(hash_file: str) -> dict[str, str] | None:
    async with Cache() as cache:
        result = await cache.check(hash_file)

        if result is not None:
            return {'report': result}

    async with DataBase() as database:
        result = await database.check_response(hash_file)

        if result is not None:
            return {'report': result}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail='Task is not completed'
    )

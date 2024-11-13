import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.db import DataBase


LLM_RESPONSE = 'text'
HASH_FILE = 'djandjas;i8732979dasldjk'
TASK_ID = 1
SALES_DATE = '1-1-24'
PRODUCT = {'name': 'book', 'quantity': 35, 'price': 300, 'category': '-'}


@pytest_asyncio.fixture()
async def mock_db(mocker):
    with patch.dict(
        'os.environ',
        {
            'DB_HOST': 'postgres',
            'DB_NAME': 'mydatabase',
            'DB_USERNAME': 'neojelll',
            'DB_PASSWORD': '123',
            'DB_PORT': '5432',
        },
    ):
        mock_session = AsyncMock()
        mocker.patch('app.db.create_async_engine', autospec=True)
        mocker.patch(
            'app.db.async_sessionmaker',
            autospec=True,
            return_value=MagicMock(return_value=mock_session),
        )
        db = DataBase()
        async with db as db_instance:
            yield db_instance, mock_session


@pytest.mark.asyncio
async def test_init_error(mocker):
    with patch.dict(
        'os.environ',
        {
            'DB_HOST': 'postgres',
            'DB_NAME': 'mydatabase',
            'DB_USERNAME': 'neojelll',
            'DB_PASSWORD': '123',
            'DB_PORT': '5432',
        },
    ):
        mocker.patch(
            'app.db.create_async_engine',
            autospec=True,
            side_effect=Exception('Error creating engine'),
        )
        mocker.patch(
            'app.db.async_sessionmaker',
            autospec=True,
            side_effect=Exception('Error creating sessionmaker'),
        )

        DataBase()


@pytest.mark.asyncio
@pytest.mark.parametrize('add_return', [None, Exception('Error')])
async def test_create_record_product(mock_db, add_return):
    db, mock_session = mock_db
    mock_session.add = MagicMock()
    if isinstance(add_return, Exception):
        mock_session.add = MagicMock(side_effect=add_return)
    mock_session.commit = AsyncMock()
    await db.create_record_product(TASK_ID, SALES_DATE, PRODUCT)
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize('add_return', [None, Exception('Error')])
async def test_create_record_task(mock_db, add_return):
    db, mock_session = mock_db
    mock_session.add = MagicMock()
    if isinstance(add_return, Exception):
        mock_session.add = MagicMock(side_effect=add_return)
    mock_session.commit = AsyncMock()
    await db.create_record_task(HASH_FILE)
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize('add_return', [None, Exception('Error')])
async def test_create_record_llm_response(mock_db, add_return):
    db, mock_session = mock_db
    mock_session.add = MagicMock()
    if isinstance(add_return, Exception):
        mock_session.add = MagicMock(side_effect=add_return)
    mock_session.commit = AsyncMock()
    await db.create_record_llm_response(TASK_ID, LLM_RESPONSE)
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_check_response_not_found(mock_db):
    db, mock_session = mock_db
    mock_session.execute = AsyncMock(return_value=None)

    result = await db.check_response(HASH_FILE)

    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_response_error(mock_db):
    db, mock_session = mock_db
    mock_session.execute = AsyncMock(side_effect=Exception('Database error'))

    result = await db.check_response(HASH_FILE)

    assert result is None
    mock_session.execute.assert_called_once()

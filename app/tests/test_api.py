from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import AsyncMock
import pytest
from app.api import app


HASH_FILE = 'abs123hash'


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_send_xml(mocker, client):
    mock_db = AsyncMock()
    mocker.patch('app.api.DataBase', autospec=True, return_value=mock_db)
    mocker.patch('app.api.process_sales_data')
    mock_db.__aenter__.return_value = mock_db
    mock_db.check_response = AsyncMock(return_value=None)
    mocker.patch('app.api.hashed_file', return_value=HASH_FILE)
    response = client.post(
        '/upload',
        files={
            'file': ('test.xml', b'<root><data>Test</data></root>', 'application/xml')
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'hash_file': HASH_FILE}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'filename, content_type, check_return, expected',
    [
        (None, 'application/xml', None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ('test.txt', 'application/xml', None, status.HTTP_400_BAD_REQUEST),
        ('test.xml', 'application/json', None, status.HTTP_400_BAD_REQUEST),
        ('test.xml', 'application/xml', 'Not None', status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_send_xml_errors(
    mocker, client, filename, content_type, check_return, expected
):
    mock_db = AsyncMock()
    mocker.patch('app.api.DataBase', autospec=True, return_value=mock_db)
    mocker.patch('app.api.process_sales_data')
    mock_db.__aenter__.return_value = mock_db
    mock_db.check_response.return_value = check_return
    mocker.patch('app.api.hashed_file', return_value=HASH_FILE)
    response = client.post(
        '/upload',
        files={'file': (filename, b'<root><data>Test</data></root>', content_type)},
    )
    assert response.status_code == expected


@pytest.mark.asyncio
async def test_get_report_hit_cache(mocker, client):
    mock_cache = AsyncMock()
    mocker.patch('app.api.Cache', return_value=mock_cache)
    mock_cache.__aenter__.return_value = mock_cache

    mock_cache.check.return_value = 'Not None'

    response = client.get(f'/report?hash_file={HASH_FILE}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'report': 'Not None'}


@pytest.mark.asyncio
async def test_get_report_hit_db(mocker, client):
    mock_db = AsyncMock()
    mocker.patch('app.api.DataBase', return_value=mock_db)
    mock_cache = AsyncMock()
    mocker.patch('app.api.Cache', return_value=mock_cache)
    mock_cache.__aenter__.return_value = mock_cache
    mock_db.__aenter__.return_value = mock_db

    mock_cache.check.return_value = None
    mock_db.check_response.return_value = 'Not None'

    response = client.get(f'/report?hash_file={HASH_FILE}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'report': 'Not None'}


@pytest.mark.asyncio
async def test_get_report_no_hit(mocker, client):
    mock_db = AsyncMock()
    mocker.patch('app.api.DataBase', return_value=mock_db)
    mock_cache = AsyncMock()
    mocker.patch('app.api.Cache', return_value=mock_cache)
    mock_cache.__aenter__.return_value = mock_cache
    mock_db.__aenter__.return_value = mock_db

    mock_cache.check.return_value = None
    mock_db.check_response.return_value = None

    response = client.get(f'/report?hash_file={HASH_FILE}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task is not completed'}

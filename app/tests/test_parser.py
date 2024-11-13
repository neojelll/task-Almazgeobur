import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.parser import parse_xml


@pytest.mark.asyncio
async def test_parse_xml_success(mocker):
    file_content = b"""
    <data date="2023-10-10">
        <products>
            <product>
                <id>1</id>
                <name>Product A</name>
                <quantity>2</quantity>
                <price>100.0</price>
                <category>Category A</category>
            </product>
        </products>
    </data>
    """

    hash_file_hex = 'hash123'

    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    mocker.patch('app.parser.DataBase', return_value=mock_db)
    mocker.patch('app.parser.Cache', return_value=mock_cache)

    mock_db.__aenter__.return_value = mock_db
    mock_cache.__aenter__.return_value = mock_cache

    mock_db.create_record_task.return_value = 1
    mock_cache.set_task_id.return_value = AsyncMock()

    result = await parse_xml(file_content, hash_file_hex)

    assert result == (
        hash_file_hex,
        1,
        '2023-10-10',
        [
            {
                'id': 1,
                'name': 'Product A',
                'quantity': 2,
                'price': 100.0,
                'category': 'Category A',
            }
        ],
    )


@pytest.mark.asyncio
async def test_parse_xml_invalid_xml(mocker):
    invalid_file_content = b'<data><products></data>'
    hash_file_hex = 'hash123'

    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    mocker.patch('app.parser.DataBase', return_value=mock_db)
    mocker.patch('app.parser.Cache', return_value=mock_cache)

    mock_db.__aenter__.return_value = mock_db
    mock_cache.__aenter__.return_value = mock_cache

    with pytest.raises(HTTPException) as exc_info:
        await parse_xml(invalid_file_content, hash_file_hex)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Server side error'


@pytest.mark.asyncio
async def test_parse_xml_db_not_hit(mocker):
    file_content = b"""
    <data date="2023-10-10">
        <products>
            <!-- No products here -->
        </products>
    </data>
    """
    hash_file_hex = 'hash123'

    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    mocker.patch('app.parser.DataBase', return_value=mock_db)
    mocker.patch('app.parser.Cache', return_value=mock_cache)

    mock_db.__aenter__.return_value = mock_db
    mock_cache.__aenter__.return_value = mock_cache

    mock_db.create_record_task.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await parse_xml(file_content, hash_file_hex)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Server side error'

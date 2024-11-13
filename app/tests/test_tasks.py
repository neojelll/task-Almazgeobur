import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock
from app.tasks import async_func


@pytest.mark.asyncio
async def test_async_func(mocker):
    mock_task = AsyncMock()
    file_content = b'<xml></xml>'
    hash_file = 'hash123'

    mocker.patch(
        'app.tasks.parse_xml',
        return_value=(
            hash_file,
            'task_id',
            '2023-10-10',
            [
                {
                    'quantity': 1,
                    'price': 100,
                    'name': 'Product A',
                    'category': 'Category A',
                }
            ],
        ),
    )
    mock_db = AsyncMock()
    mocker.patch('app.tasks.DataBase', return_value=mock_db)
    mock_db.__aenter__.return_value = mock_db
    mock_db.create_record_llm_response = AsyncMock()
    mocker.patch('app.tasks.send_prompt_to_llm_api', return_value='Expected response')
    mock_cache = AsyncMock()
    mocker.patch('app.tasks.Cache', return_value=mock_cache)
    mock_cache.__aenter__.return_value = mock_cache
    mock_cache.delete_task_id = AsyncMock()
    mock_cache.set_llm_response = AsyncMock()

    await async_func(mock_task, file_content, hash_file)
    assert mock_task.update_state.call_count == 4
    mock_cache.delete_task_id.assert_awaited_once_with('task_id')
    mock_cache.set_llm_response.assert_awaited_once_with(hash_file, 'Expected response')


@pytest.mark.asyncio
async def test_async_func_error(mocker):
    mock_task = AsyncMock()
    file_content = b'<xml></xml>'
    hash_file = 'hash123'

    mocker.patch(
        'app.tasks.parse_xml',
        return_value=(
            hash_file,
            'task_id',
            '2023-10-10',
            [
                {
                    'quantity': 1,
                    'price': 100,
                    'name': 'Product A',
                    'category': 'Category A',
                }
            ],
        ),
    )
    mock_db = AsyncMock()
    mocker.patch('app.tasks.DataBase', return_value=mock_db)
    mock_db.__aenter__.return_value = mock_db
    mock_db.create_record_llm_response = AsyncMock()
    mocker.patch('app.tasks.send_prompt_to_llm_api', return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await async_func(mock_task, file_content, hash_file)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Server side error'

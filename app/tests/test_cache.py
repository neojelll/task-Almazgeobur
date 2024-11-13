import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app.cache import Cache


LLM_RESPONSE = 'text'
HASH_FILE = 'djandjas;i8732979dasldjk'
TASK_ID = 1


@pytest_asyncio.fixture()
async def mock_cache(mocker):
    with patch.dict(
        'os.environ', {'CACHE_HOST': 'redis', 'CACHE_PORT': '6379', 'CACHE_TTL': '3600'}
    ):
        mock_session = AsyncMock()
        mocker.patch('app.cache.Redis', autospec=True, return_value=mock_session)
        cache = Cache()
        async with cache as cache_instance:
            yield cache_instance, mock_session


@pytest.mark.asyncio
async def test_init_error(mocker):
    with patch.dict('os.environ', {'CACHE_HOST': 'redis', 'CACHE_PORT': '6379'}):
        mocker.patch('app.cache.Redis', autospec=True, side_effect=Exception('Error'))
        Cache()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'exists_return, get_return, expected',
    [(True, 'True', 'True'), (True, Exception('Error'), None), (False, '', None)],
)
async def test_check(mock_cache, exists_return, get_return, expected):
    hash_file = 'dlapa1928doalxpa'
    cache, mock_session = mock_cache
    mock_session.exists = AsyncMock(return_value=exists_return)
    if isinstance(get_return, Exception):
        mock_session.get = AsyncMock(side_effect=get_return)
    else:
        mock_session.get = AsyncMock(return_value=get_return)
    result = await cache.check(hash_file)
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize('set_return', [None, Exception('Error')])
async def test_set_task_id(mock_cache, set_return):
    cache, mock_session = mock_cache
    if isinstance(set_return, Exception):
        mock_session.set = AsyncMock(side_effect=set_return)
    await cache.set_task_id(TASK_ID, HASH_FILE)
    mock_session.set.assert_called_once_with(str(TASK_ID), HASH_FILE)


@pytest.mark.asyncio
@pytest.mark.parametrize('delete_return', [None, Exception('Error')])
async def test_delete_task_id(mock_cache, delete_return):
    cache, mock_session = mock_cache
    if isinstance(delete_return, Exception):
        mock_session.delete = AsyncMock(side_effect=delete_return)
    await cache.delete_task_id(TASK_ID)
    mock_session.delete.assert_called_once_with(str(TASK_ID))


@pytest.mark.asyncio
@pytest.mark.parametrize('set_return', [None, Exception('Error')])
async def test_set_llm_response(mock_cache, set_return):
    cache, mock_session = mock_cache
    if isinstance(set_return, Exception):
        mock_session.set = AsyncMock(side_effect=set_return)
    await cache.set_llm_response(HASH_FILE, LLM_RESPONSE)
    mock_session.set.assert_called_once_with(HASH_FILE, LLM_RESPONSE, ex=3600)

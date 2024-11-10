from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


chat = GigaChat(
    credentials=os.getenv('GIGACHAT_API_KEY'), scope='GIGACHAT_API_PERS', streaming=True
)


async def send_prompt_to_claude_api(prompt: str):
    try:
        logger.debug(f'Start response to gigachat API with params: {prompt}')
        messages = [
            SystemMessage(
                content='Составь краткий аналитический отчет с выводами и рекомендациями.'
            ),
            HumanMessage(content=prompt),
        ]
        res = chat(messages)
        messages.append(res)
        logger.debug('Completed response to gigachat API')
        return res.content
    except Exception as e:
        logger.error(f'Error when response to gigachat API: {e}')

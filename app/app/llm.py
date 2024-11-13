import os
from loguru import logger
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from .logger import configure_logger


configure_logger()


chat = GigaChat(
    credentials=os.getenv('GIGACHAT_API_KEY'),
    verify_ssl_certs=False,
    scope='GIGACHAT_API_PERS',
    streaming=True,
)


async def send_prompt_to_llm_api(prompt: str):
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

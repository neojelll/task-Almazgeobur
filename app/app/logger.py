import sys
from loguru import logger


def configure_logger() -> None:
    logger.remove()

    logger.add(
        sys.stderr,
        format='{time:YYYY-MM-DD at HH:mm:ss} <level>{level}</level> <red>{name}</red>: <red>{function}</red>({line}) - <cyan>{message}</cyan>',
        level='DEBUG',
    )

    logger.add(
        'app.log',
        format='{time:YYYY-MM-DD at HH:mm:ss} {level} {name}: {function}({line}) - {message}',
        level='DEBUG',
    )

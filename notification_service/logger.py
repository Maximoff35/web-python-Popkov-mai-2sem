import logging
import sys


def setup_logging() -> None:
    """
    Настраивает централизованное логирование для notification service.
    Вызывается один раз при старте.
    Модули используют logging.getLogger(__name__).
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
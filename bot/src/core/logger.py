"""Настройка логирования с поддержкой таймзон."""

import sys
import logging
from datetime import datetime

from core.config import get_settings


class TZFormatter(logging.Formatter):
    """Кастомный форматтер для логов с временем в указанной таймзоне."""

    def __init__(self, fmt: str = None, datefmt: str = None, style: str = "%", tz=None):
        super().__init__(fmt, datefmt, style)
        self.tz = tz

    def formatTime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        tz_time = datetime.fromtimestamp(timestamp=record.created, tz=self.tz)

        if datefmt:
            return tz_time.strftime(datefmt)
        return tz_time.strftime("%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        """Переопределяем format для правильной обработки UTF-8."""
        formatted = super().format(record)

        if isinstance(formatted, str):
            try:
                formatted.encode("utf-8")
                return formatted
            except UnicodeEncodeError:
                return formatted.encode("utf-8", errors="replace").decode("utf-8")

        return formatted


def setup_logger(
    name: str,
    level: str = "INFO",
    settings=get_settings(),
) -> logging.Logger:
    """Создать и настроить логгер."""
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(level.upper())

    formatter = TZFormatter(
        fmt="[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s",
        tz=settings.timezone,
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.propagate = False

    sys.stdout.flush()
    sys.stderr.flush()

    return logger

import sys

from loguru import logger

from core.logs.handlers import UvicornHandler

__all__ = ["UvicornHandler", "configure_logger", "get_uvicorn_log_config"]


def configure_logger() -> None:
    log_format_all = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> {exception}\n"
    log_format_request = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message} {exception}\n"
    )

    def log_format(record: "Record") -> str:  # type: ignore  # noqa: F821
        if record["level"].name == "REQUEST":
            return log_format_request
        return log_format_all

    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
        diagnose=True,
        backtrace=False,
    )
    logger.level("DEBUG", color="<fg #7f7f7f>")
    logger.level("INFO", color="<white>")
    logger.level("SUCCESS", color="<green>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    logger.level("CRITICAL", color="<bold><white><RED>")
    logger.level("REQUEST", no=38, color="<magenta>")


def get_uvicorn_log_config() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
        },
        "handlers": {
            "default": {
                "()": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "uvicorn": {
                "()": "core.logs.handlers.UvicornHandler",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["uvicorn"], "level": "INFO"},
        },
    }

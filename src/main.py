import uvicorn
from loguru import logger

from core.logs import configure_logger, get_uvicorn_log_config
from core.settings_model import settings


def main() -> None:
    configure_logger()
    logger.info("Starting app...")

    uvicorn.run(
        "app.app:app",
        log_config=get_uvicorn_log_config(),
        port=80,
        host="0.0.0.0",  # noqa: S104
        workers=settings.server.workers,
    )


if __name__ == "__main__":
    main()

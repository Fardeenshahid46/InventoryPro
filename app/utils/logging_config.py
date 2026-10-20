import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


def setup_logging(app):
    """Configure structured logging with file rotation and console output."""
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_file_path = Path(app.config.get("LOG_FILE", "logs/inventory_pro.log"))
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s"
    )

    # Rotating file handler (max 10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Attach to Flask logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Also attach to root logger for capturing third-party warnings
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

"""Error Logging Module"""
import logging
import logging.handlers

try:
    logger = logging.getLogger("main")
    logger.setLevel(logging.ERROR)
    fh = logging.handlers.RotatingFileHandler(filename="error.log",
                                                maxBytes=10485760,
                                                backupCount=10)
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

except Exception as error:
    logger.error("Logger:Main %s", error)
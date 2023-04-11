from loguru import logger
import sys

logger.remove()
logger.level("system", no=38, color="<yellow>")
_ = logger.add(
    sys.stderr,
    format="<b><yellow>{level}</yellow></b>: {message}",
    filter=lambda record: record["level"].name == "system",
)

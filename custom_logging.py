from loguru import logger
import sys

logger.remove()
logger.level("system", no=38, color="<yellow>")
_ = logger.add(
    sys.stderr,
    format="<b><yellow>{level}</yellow></b>: {message}",
    filter=lambda record: record["level"].name == "system",
)
logger.level("danger", no=38, color="<red>")
_ = logger.add(
    sys.stderr,
    format="<b><red>DANGER</red></b>: {message}",
    filter=lambda record: record["level"].name == "danger",
)

# more "intuitive" fucntion to call the logger

log_types = ["system", "danger"]

for log_type in log_types:
    exec(
        f"""
def {log_type}(message: str):
    logger.log("{log_type}", message)
"""
    )

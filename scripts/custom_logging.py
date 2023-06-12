from loguru import logger
from sys import stderr

logger.remove()
logger.level("system", no=38, color="<yellow>")
_ = logger.add(
    stderr,
    format="<b><yellow>{level}</yellow></b>: {message}",
    filter=lambda record: record["level"].name == "system",
)
logger.level("danger", no=1, color="<red>")
_ = logger.add(
    stderr,
    format="<b><red>DANGER</red></b>: {message}",
    filter=lambda record: record["level"].name == "danger",
)
logger.level("error", no=2, color="<red>")
_ = logger.add(
    stderr,
    format="<b><red>ERROR</red></b>: {message}",
    filter=lambda record: record["level"].name == "error",
)

# more "intuitive" fucntion to call the logger
log_types = ["system", "danger", "error"]

for log_type in log_types:
    exec(
        f"""
def {log_type}(message: str):
    logger.log("{log_type}", message)
"""
    )
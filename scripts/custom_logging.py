from loguru import logger
from sys import stderr
from config import script_dir

logger.remove()
logger.level("hint", no=5, color="<yellow>")
_ = logger.add(
    stderr,
    format="<b><yellow>{level}</yellow></b>: {message}",
    filter=lambda record: record["level"].name == "hint",
)
logger.level("system", no=38, color="<yellow>")
_ = logger.add(
    stderr,
    format="<b><yellow>{level}</yellow></b>: {message}",
    filter=lambda record: record["level"].name == "system",
)
logger.level("command", no=38, color="<green>")
_ = logger.add(
    stderr,
    format="<b><green>{level}</green></b>: {message}",
    filter=lambda record: record["level"].name == "command",
)
logger.level("danger", no=99, color="<red>")
_ = logger.add(
    stderr,
    format="<b><red>DANGER</red></b>: {message}",
    filter=lambda record: record["level"].name == "danger",
)
logger.level("error", no=100, color="<red>")
_ = logger.add(
    stderr,
    format="<b><red>ERROR</red></b>: {message}",
    filter=lambda record: record["level"].name == "error",
)

logger.add(f"{script_dir}/log/errors.log", level="error", rotation="500 MB")

# more "intuitive" fucntion to call the logger
log_types = ["system", "danger", "error", "command", "hint"]

for log_type in log_types:
    exec(
        f"""
def {log_type}(message: str):
    logger.log("{log_type}", message)
"""
    )

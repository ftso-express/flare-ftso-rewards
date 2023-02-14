import logging
from rich.logging import RichHandler

# Global setting
logging.basicConfig(
    level="INFO",
    # level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
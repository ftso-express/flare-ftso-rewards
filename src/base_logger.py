import logging
from rich.logging import RichHandler


#File to log to
logFile = './logs/data.log'
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s', 
                datefmt='%d/%m/%Y %H:%M:%S')

#Setup File handler
file_handler = logging.FileHandler(logFile)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

#Setup Rich handler
rich_handler = RichHandler(rich_tracebacks=True)
rich_handler.setLevel(logging.INFO)

# Global setting
logging.basicConfig(
    level="WARNING",
    # level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    # handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger(__name__)

log.addHandler(file_handler)
log.addHandler(rich_handler)
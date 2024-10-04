import logging
from logging.handlers import RotatingFileHandler
import os


################# CONFIG ##############
log_directory = "/path/to/your/log/directory"
logfile_name = "monitoreo_elastic.log"
######################################

# Create the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)

# Define the log file path
log_file = os.path.join(log_directory, logfile_name)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a rotating file handler
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,  # Keep up to 5 backup files
)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Optionally, add a stream handler to also log to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
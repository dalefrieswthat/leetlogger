import os
import sys
import logging
from datetime import datetime

# Set up logging
log_file = 'leetlogger.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("Starting LeetLogger")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
logging.info("Files in current directory:")
for file in os.listdir('.'):
    logging.info(f"  {file}")

try:
    import main
    logging.info("Successfully imported main module")
    main.main()
except Exception as e:
    logging.error(f"Error running application: {str(e)}", exc_info=True) 
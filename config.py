import logging
import os


UNEMPLOYED_COL_NAME = "unemployment_count"
SHEET_NAME = "NUTS3"
DATABASE_URL = f"postgres://postgres:{os.getenv('db_password', 'epic_password')}@localhost/cz_unemployment"
print(DATABASE_URL)
# DATABASE_URL = 'sqlite:///:memory:'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# logging.basicConfig(level=logging.DEBUG)
MY_LOGGER = logging.getLogger(__name__)
DATA_GETTER_LOGGER = logging.getLogger(__name__)
# c_handler = logging.StreamHandler()
# c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# MY_LOGGER.addHandler(c_handler)

file_handler = logging.FileHandler("log.log")
file_format = logging.Formatter('[%(asctime)s] --- %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
MY_LOGGER.addHandler(file_handler)

data_getter_file_handler = logging.FileHandler(ROOT_DIR + "\\getting_data\\log.log")
data_getter_file_format = logging.Formatter('[%(asctime)s] --- %(levelname)s - %(message)s')
data_getter_file_handler.setFormatter(data_getter_file_format)
DATA_GETTER_LOGGER.addHandler(data_getter_file_handler)

from dotenv import load_dotenv
import os


load_dotenv()

# general
DATA_PATH = os.getenv("DATA_PATH")
WAF_ENDPOINT = os.getenv("WAF_ENDPOINT")

# cAdvisor
WAF_CONTAINER_NAME = os.getenv("WAF_CONTAINER_NAME")
CADVISOR_ENDPOINT = os.getenv("CADVISOR_ENDPOINT")

# FTW
FTW_TEST_FILE_PATH = os.getenv("FTW_TEST_FILE_PATH")
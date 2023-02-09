import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6369")
QUEUES = ["emails","default"]

# rq work -c settings
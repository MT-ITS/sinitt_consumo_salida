import configparser
import os
from setuptools import setup, find_packages
from dotenv import load_dotenv
import sys

load_dotenv()
# setup(name='ingest_server', version='1.0', packages=find_packages())

config = configparser.ConfigParser()

running_profile = os.getenv("running_profile")

config.read("config/config_" + running_profile + ".ini")
print("config/config_" + running_profile + ".ini")

postgres_host = config["Postgres"]["postgres_host"]
postgres_port = config["Postgres"]["postgres_port"]
postgres_user = config["Postgres"]["postgres_user"]
postgres_db = config["Postgres"]["postgres_db"]
postgres_password = config["Postgres"]["postgres_password"]
sqlalchemy_pg = "postgresql://{user}:{password}@{hostname}:{port}/{database}".format(
    password=postgres_password,
    user=postgres_user,
    hostname=postgres_host,
    port=postgres_port,
    database=postgres_db,
)
sqlalchmey_session_table = config["Postgres"]["session_table"]
postgres_pool_size = int(config["Postgres"]["postgres_pool_size"])

DATEX_PAYLOAD = "D2Payload"
DATEX_MESSAGE_CONTAINER = "D2MessageContainer"

secret_key = config["Token"]["random_token"]

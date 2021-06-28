import os
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_ACCESS_ID = config["app"]["TELEGRAM_ACCESS_ID"]

MEMORIZATION_TRESHOLD = int(config["app"]["MEMORIZATION_TRESHOLD"])

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = config["app"]["DB_NAME"]
import os
import json
import logging
import time

import pandas as pd
import requests
from requests.exceptions import HTTPError, Timeout
from simple_chalk import blue, green, red, yellow

from salt import hash_pii
from src.storage import (
    add_user_to_redis,
    check_table_exists,
    create_address_table,
    create_user_table,
    insert_into_address_table,
    insert_into_user_table,
)
from validate import validate_json

# Configuration
BATCH_SIZE = int(os.getenv("DATA_BATCH_SIZE", "10"))
INTERVAL = int(os.getenv("FETCH_INTERVAL_SECONDS", "120"))
API_URL = f"https://randomuser.me/api/?results={BATCH_SIZE}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - line:%(lineno)d - %(filename)s:%(funcName)s -> %(message)s",
)

def get_user_data() -> list:
    try:
        logging.info(blue(f"Fetching {BATCH_SIZE} users from API..."))
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        raw_data = response.json()
        return raw_data.get("results", [])

    except (HTTPError, Timeout, requests.RequestException) as e:
        logging.error(red(f"API Error: {e}"))
        return []

def extract_user_data_for_storage(data: list) -> list:
    user_data = []
    for u in data:
        try:
            user = {
                "uid": u["login"]["uuid"],
                "password": u["login"].get("password", "n/a"),
                "first_name": u["name"].get("first", "n/a"),
                "last_name": u["name"].get("last", "n/a"),
                "username": u["login"].get("username", "n/a"),
                "email": u.get("email", "n/a"),
                "phone_number": u.get("phone", "n/a"),
                "social_insurance_number": hash_pii(
                    u.get("id", {}).get("value") or "N/A"
                ),
                "date_of_birth": u.get("dob", {}).get("date", "n/a")[:10],
            }
            user_data.append(user)
        except (KeyError, TypeError) as e:
            logging.error(red(f"Error mapping user data: {e}"))
            continue
    return user_data

def extract_address_data_for_storage(data: list) -> list:
    address_data = []
    for a in data:
        try:
            address = {
                "uid": a["login"]["uuid"],
                "city": a.get("location", {}).get("city", "n/a"),
                "street_name": a.get("location", {}).get("street", {}).get("name", "n/a"),
                "street_address": str(a.get("location", {}).get("street", {}).get("number", "n/a")),
                "zip_code": str(a.get("location", {}).get("postcode", "n/a")),
                "state": a.get("location", {}).get("state", "n/a"),
                "country": a.get("location", {}).get("country", "n/a"),
            }
            address_data.append(address)
        except (KeyError, TypeError) as e:
            logging.error(red(f"Error mapping address data: {e}"))
            continue
    return address_data

def main() -> None:
    logging.info(green("Starting ETL Pipeline..."))
    while True:
        try:
            data_to_be_processed = get_user_data()
            if not data_to_be_processed:
                logging.warning(yellow("No data received. Retrying in next cycle..."))
                time.sleep(INTERVAL)
                continue

            user_data = extract_user_data_for_storage(data_to_be_processed)
            users_address_data = extract_address_data_for_storage(data_to_be_processed)

            add_user_to_redis(user_data, users_address_data)

            if not check_table_exists("users") or not check_table_exists("users_address"):
                if create_user_table():
                    logging.info(yellow("users table was created"))
                if create_address_table():
                    logging.info(yellow("users_address table was created"))

            for user in user_data:
                if insert_into_user_table(user):
                    logging.info(f"User: {blue(user['uid'])} added to Postgres")

            for address in users_address_data:
                if insert_into_address_table(address):
                    logging.info(f"User: {blue(address['uid'])} address added to Postgres")

            logging.info(green(f"Successfully processed {len(user_data)} users."))
        except Exception as e:
            logging.error(red(f"Critical error in ETL loop: {e}"))

        logging.info(yellow(f"Sleeping for {INTERVAL} seconds..."))
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

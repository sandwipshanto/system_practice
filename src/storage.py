import os
import logging
from datetime import datetime
from typing import Literal

import psycopg2
import redis
from redis import RedisError
from simple_chalk import red, green, yellow

# Load configuration from environment
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - line:%(lineno)d - %(message)s",
)

# REDIS connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def add_user_to_redis(user_data: list, user_address_data: list) -> None:
    try:
        for ud, uad in zip(user_data, user_address_data):
            uid: str = ud.get("uid")
            users_data: dict = {
                "password": ud.get("password", "n/a"),
                "first_name": ud.get("first_name", "n/a"),
                "last_name": ud.get("last_name", "n/a"),
                "username": ud.get("username", "n/a"),
                "email": ud.get("email", "n/a"),
                "phone_number": ud.get("phone_number", "n/a"),
                "social_insurance_number": ud.get("social_insurance_number", "n/a"),
                "date_of_birth": ud.get("date_of_birth", "n/a"),
            }

            address_data: dict = {
                "city": uad.get("city", "n/a"),
                "street_name": uad.get("street_name", "n/a"),
                "street_address": uad.get("street_address", "n/a"),
                "zip_code": uad.get("zip_code", "n/a"),
                "state": uad.get("state", "n/a"),
                "country": uad.get("country", "n/a"),
            }

            full_user_data: dict = users_data | address_data

            # Add user to Redis
            redis_client.hset(uid, mapping=full_user_data)

            # Set TTL in Redis for 2 min
            redis_client.expire(uid, 120)

        logging.info(
            f"{red(len(user_data))} Users have been cached in Redis, with a TTL of 2 mins"
        )

    except ValueError as e:
        raise e


def get_user_from_redis(key: str) -> dict:
    try:
        data = {}

        if redis_client.exists(key):
            data: dict = redis_client.hgetall(key)
        else:
            logging.error(f"Key {red(key)} not found in Redis. Trying Postgres...")

        return data

    except RedisError as e:
        logging.error(f"General Redis error: {e}")
        raise e


def create_user_table() -> Literal[True]:
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        CREATE TABLE IF NOT EXISTS users
                            (
                                uid VARCHAR(255) PRIMARY KEY,
                                password VARCHAR(255),
                                first_name VARCHAR(255),
                                last_name VARCHAR(255),
                                username VARCHAR(255),
                                email VARCHAR(255),
                                phone_number VARCHAR(255),
                                social_insurance_number VARCHAR(255),
                                date_of_birth VARCHAR(255),
                                ts INT
                            );
                    """
                )

    except Exception as e:
        logging.error(red(e))

    return True


def create_address_table() -> Literal[True]:
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        CREATE TABLE IF NOT EXISTS users_address
                            (
                                uid VARCHAR(255),
                                city VARCHAR(255),
                                street_name VARCHAR(255),
                                street_address VARCHAR(255),
                                zip_code VARCHAR(255),
                                state VARCHAR(255),
                                country VARCHAR(255),
                                ts INT,

                                PRIMARY KEY (uid),
                                FOREIGN KEY (uid) REFERENCES users(uid)
                            );
                    """
                )

    except Exception as e:
        logging.error(red(e))

    return True


def check_table_exists(table_name):
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' AND table_name = %s
                        );
                    """,
                    (table_name,),
                )
                result = curs.fetchone()
                return result[0] if result is not None else False
    except psycopg2.Error as e:
        logging.error(red(e))
        return False


def insert_into_user_table(user_data: dict) -> Literal[True]:
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        INSERT INTO users (
                            uid, password, first_name, last_name, username, email, phone_number, social_insurance_number, date_of_birth, ts
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        );
                    """,
                    (
                        user_data["uid"],
                        user_data["password"],
                        user_data["first_name"],
                        user_data["last_name"],
                        user_data["username"],
                        user_data["email"],
                        user_data["phone_number"],
                        user_data["social_insurance_number"],
                        user_data["date_of_birth"],
                        int(datetime.timestamp(datetime.now())),
                    ),
                )

    except Exception as e:
        logging.error(red(e))

    return True


def insert_into_address_table(address_data: dict) -> Literal[True]:
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        INSERT INTO users_address (
                            uid, city, street_name, street_address, zip_code, state, country, ts
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        );
                    """,
                    (
                        address_data["uid"],
                        address_data["city"],
                        address_data["street_name"],
                        address_data["street_address"],
                        address_data["zip_code"],
                        address_data["state"],
                        address_data["country"],
                        int(datetime.timestamp(datetime.now())),
                    ),
                )

    except Exception as e:
        logging.error(red(e))

    return True

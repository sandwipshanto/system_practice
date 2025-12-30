import os
import logging

import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.storage import get_user_from_redis

# Load configuration from environment
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - line:%(lineno)d - %(message)s",
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "I am Root"}


@app.get("/api/v2/datapipeline/list-users")
async def list_users():
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                    SELECT uid FROM users ORDER BY ts DESC;
                    """
                )
                return curs.fetchall()
    except psycopg2.Error as e:
        return {"message": str(e)}


@app.get("/api/v2/datapipeline/{user_id}")
async def get_user(user_id: str):
    # Check length of Redis first before checking Postgres
    redis = get_user_from_redis(user_id)

    if len(redis) != 0:
        return redis
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                        SELECT
                            users.uid,
                            first_name,
                            last_name,
                            username,
                            email,
                            phone_number,
                            social_insurance_number,
                            date_of_birth,
                            city,
                            street_name,
                            street_address,
                            zip_code,
                            state,
                            country
                        FROM users
                        JOIN users_address UA ON users.uid = UA.uid
                        WHERE users.uid = %s;
                        """,
                    (user_id,),
                )

                return curs.fetchall()
    except psycopg2.Error as e:
        return {"message": str(e)}

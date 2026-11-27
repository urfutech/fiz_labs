from typing import Annotated

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
import psycopg2
from psycopg2.extras import RealDictCursor


try:
    conn = psycopg2.connect(
        host="localhost",
        database="fiz_labs",
        user="postgres",
        password="",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("Database connection success")
except Exception as error:
    print("Connect to database failed")
    print("Error: ", error)


def show_all_users():
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        print(row)

    print("That's all")

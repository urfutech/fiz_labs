from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    is_published = Column(Boolean, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    role = Column(String(16), nullable=False)
    login = Column(String(128), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    middle_name = Column(String(64), nullable=False)
    group_id = Column(Integer)
    selectable_for_students = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    status = Column(String(16), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

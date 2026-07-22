from sqlalchemy import Column, Integer, String, Table

from flask_mvc.middlewares.base_model import BaseModel
from tests.app import db

messages_table = Table(
    "messages",
    db.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(100), nullable=False),
)


class Message(BaseModel, db.Model):
    __tablename__ = "messages"

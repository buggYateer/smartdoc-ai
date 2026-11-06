from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from settings import DATABASE_URL

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass

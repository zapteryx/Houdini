# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Ban(Base):
    __tablename__ = 'bans'

    ID = Column(Integer, primary_key=True)
    Moderator = Column(Text, nullable=False)
    Player = Column(Integer, nullable=False)
    Comment = Column(Text, nullable=False)
    Expiration = Column(Integer, nullable=False)
    Time = Column(Integer, nullable=False)
# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Igloo(Base):
    __tablename__ = 'igloos'

    ID = Column(Integer, primary_key=True)
    Owner = Column(Integer, nullable=False)
    Type = Column(Integer, nullable=False, server_default=text("'1'"))
    Floor = Column(Integer, nullable=False, server_default=text("'0'"))
    Music = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Furniture = Column(Text, nullable=False)
    Locked = Column(Integer, nullable=False, server_default=text("'1'"))

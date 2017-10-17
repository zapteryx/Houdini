# coding: utf-8
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Puffle(Base):
    __tablename__ = 'puffles'

    ID = Column(Integer, primary_key=True)
    Owner = Column(Integer, nullable=False)
    Name = Column(String(12), nullable=False)
    AdoptionDate = Column(Integer, nullable=False)
    Type = Column(Integer, nullable=False)
    Food = Column(Integer, nullable=False, server_default=text("'100'"))
    Play = Column(Integer, nullable=False, server_default=text("'100'"))
    Rest = Column(Integer, nullable=False, server_default=text("'100'"))
    Clean = Column(Integer, nullable=False, server_default=text("'100'"))
    Walking = Column(Integer, server_default=text("'0'"))
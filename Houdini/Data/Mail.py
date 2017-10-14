# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Mail(Base):
    __tablename__ = 'postcards'

    ID = Column(Integer, primary_key=True)
    Recipient = Column(Integer, nullable=False)
    SenderName = Column(String(12), nullable=False)
    SenderID = Column(Integer, nullable=False)
    Details = Column(VARCHAR(12), nullable=False)
    Date = Column(Integer, nullable=False)
    Type = Column(SmallInteger, nullable=False)
    HasRead = Column(Boolean, nullable=False, server_default='0')
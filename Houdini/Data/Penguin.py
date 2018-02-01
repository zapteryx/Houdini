# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, String, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Penguin(Base):
    __tablename__ = 'penguins'

    ID = Column(Integer, primary_key=True)
    Username = Column(String(12), nullable=False, unique=True)
    Nickname = Column(String(16), nullable=False)
    Password = Column(String(255), nullable=False)
    LoginKey = Column(String(32), nullable=False)
    Email = Column(String(254), nullable=False)
    RegistrationDate = Column(Integer, nullable=False)
    LastPaycheck = Column(Integer, nullable=False)
    Moderator = Column(Integer, nullable=False, server_default=text("'0'"))
    Inventory = Column(Text, nullable=False)
    Coins = Column(Integer, nullable=False, server_default=text("'200000'"))
    Igloo = Column(Integer, nullable=False)
    Igloos = Column(Text, nullable=False)
    Floors = Column(Text, nullable=False)
    Furniture = Column(Text, nullable=False)
    Buddies = Column(Text, nullable=False)
    Ignore = Column(Text, nullable=False)
    Color = Column(Integer, nullable=False, server_default=text("'1'"))
    Head = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Face = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Neck = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Body = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Hand = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Feet = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Photo = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Flag = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Walking = Column(Integer, nullable=False, server_default=text("'0'"))
    Banned = Column(String(20), nullable=False, server_default=text("'0'"))
    Stamps = Column(Text, nullable=False)
    RecentStamps = Column(Text, nullable=False)
    StampBook = Column(Text, nullable=False, server_default=text("'1%1%0%1'"))
    EPF = Column(String(9), nullable=False, server_default=text("'0,0,0'"))
    NinjaRank = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    NinjaProgress = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    Deck = Column(Text, nullable=False, server_default=text("'1,1|6,1|9,1|14,1|17,1|20,1|22,1|23,1|26,1|73,1|89,1|81,1'"))
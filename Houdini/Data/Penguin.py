# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class Penguin(Base):
    __tablename__ = 'penguin'

    ID = Column(Integer, primary_key=True)
    Username = Column(String(12), nullable=False, unique=True)
    Nickname = Column(String(24), nullable=False)
    Password = Column(String(255), nullable=False)
    LoginKey = Column(String(255), server_default=text("''"))
    ConfirmationHash = Column(String(255), server_default=text("''"))
    Email = Column(String(255), nullable=False, index=True)
    RegistrationDate = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    Active = Column(SmallInteger, nullable=False, server_default=text("0"))
    SafeChat = Column(SmallInteger, nullable=False, server_default=text("0"))
    Igloo = Column(Integer, nullable=False, server_default=text("0"))
    LastPaycheck = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    MinutesPlayed = Column(Integer, nullable=False, server_default=text("0"))
    Moderator = Column(SmallInteger, nullable=False, server_default=text("0"))
    MascotStamp = Column(Integer, nullable=False, server_default=text("0"))
    Avatar = Column(SmallInteger, nullable=False, server_default=text("0"))
    Coins = Column(Integer, nullable=False, server_default=text("1000000"))
    Color = Column(Integer, nullable=False, server_default=text("1"))
    Head = Column(Integer, nullable=False, server_default=text("0"))
    Face = Column(Integer, nullable=False, server_default=text("0"))
    Neck = Column(Integer, nullable=False, server_default=text("0"))
    Body = Column(Integer, nullable=False, server_default=text("0"))
    Hand = Column(Integer, nullable=False, server_default=text("0"))
    Feet = Column(Integer, nullable=False, server_default=text("0"))
    Photo = Column(Integer, nullable=False, server_default=text("0"))
    Flag = Column(Integer, nullable=False, server_default=text("0"))
    Permaban = Column(SmallInteger, nullable=False, server_default=text("0"))
    BookModified = Column(SmallInteger, nullable=False, server_default=text("0"))
    BookColor = Column(SmallInteger, nullable=False, server_default=text("1"))
    BookHighlight = Column(SmallInteger, nullable=False, server_default=text("1"))
    BookPattern = Column(SmallInteger, nullable=False, server_default=text("0"))
    BookIcon = Column(SmallInteger, nullable=False, server_default=text("1"))
    AgentStatus = Column(SmallInteger, nullable=False, server_default=text("0"))
    FieldOpStatus = Column(SmallInteger, nullable=False, server_default=text("0"))
    CareerMedals = Column(Integer, nullable=False, server_default=text("0"))
    AgentMedals = Column(Integer, nullable=False, server_default=text("0"))
    LastFieldOp = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    NinjaRank = Column(SmallInteger, nullable=False, server_default=text("0"))
    NinjaProgress = Column(SmallInteger, nullable=False, server_default=text("0"))
    FireNinjaRank = Column(SmallInteger, nullable=False, server_default=text("0"))
    FireNinjaProgress = Column(SmallInteger, nullable=False, server_default=text("0"))
    WaterNinjaRank = Column(SmallInteger, nullable=False, server_default=text("0"))
    WaterNinjaProgress = Column(SmallInteger, nullable=False, server_default=text("0"))
    SnowNinjaRank = Column(SmallInteger, nullable=False, server_default=text("0"))
    SnowNinjaProgress = Column(SmallInteger, nullable=False, server_default=text("0"))
    NinjaMatchesWon = Column(Integer, nullable=False, server_default=text("0"))
    FireMatchesWon = Column(Integer, nullable=False, server_default=text("0"))
    WaterMatchesWon = Column(Integer, nullable=False, server_default=text("0"))
    SnowMatchesWon = Column(Integer, nullable=False, server_default=text("0"))
    RainbowAdoptability = Column(Integer, nullable=False, server_default=text("0"))
    HasDug = Column(Integer, nullable=False, server_default=text("0"))
    Nuggets = Column(Integer, nullable=False, server_default=text("0"))

    parents = relationship(
        u'Penguin',
        secondary='buddy_list',
        primaryjoin=u'Penguin.ID == buddy_list.c.BuddyID',
        secondaryjoin=u'Penguin.ID == buddy_list.c.PenguinID'
    )
    parents1 = relationship(
        u'Penguin',
        secondary='ignore_list',
        primaryjoin=u'Penguin.ID == ignore_list.c.IgnoreID',
        secondaryjoin=u'Penguin.ID == ignore_list.c.PenguinID'
    )


class IgnoreList(Base):
    __tablename__ = 'ignore_list'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False)
    IgnoreID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                      nullable=False, index=True)

class BuddyList(Base):
    __tablename__ = 'buddy_list'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False)
    BuddyID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                     nullable=False, index=True)
    Type = Column(SmallInteger, nullable=False, server_default=text("0"))

class NameApproval(Base):
    __tablename__ = 'name_approval'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False)
    en = Column(SmallInteger, nullable=False, server_default=text("0"))
    pt = Column(SmallInteger, nullable=False, server_default=text("0"))
    fr = Column(SmallInteger, nullable=False, server_default=text("0"))
    es = Column(SmallInteger, nullable=False, server_default=text("0"))
    de = Column(SmallInteger, nullable=False, server_default=text("0"))
    ru = Column(SmallInteger, nullable=False, server_default=text("0"))

class Inventory(Base):
    __tablename__ = 'inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    ItemID = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')


class IglooInventory(Base):
    __tablename__ = 'igloo_inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    IglooID = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')


class FurnitureInventory(Base):
    __tablename__ = 'furniture_inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    FurnitureID = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))
    Quantity = Column(SmallInteger, nullable=False, server_default=text("1"))

    penguin = relationship(u'Penguin')

class FloorInventory(Base):
    __tablename__ = 'floor_inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    FloorID = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')

class LocationInventory(Base):
    __tablename__ = 'location_inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    LocationID = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')

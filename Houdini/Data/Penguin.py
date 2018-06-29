# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, Table, text

from Houdini.Data import metadata, RowProxyDictionary

Penguin = Table(
    'penguin', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Username', String(12), nullable=False, unique=True),
    Column('Nickname', String(12), nullable=False),
    Column('Approval', Integer, nullable=False, server_default=text("0")),
    Column('Password', String(255), nullable=False),
    Column('LoginKey', String(255), server_default=text("''")),
    Column('Email', String(255), nullable=False, index=True),
    Column('RegistrationDate', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('Active', Integer, nullable=False, server_default=text("0")),
    Column('LastPaycheck', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('MinutesPlayed', Integer, nullable=False, server_default=text("0")),
    Column('Moderator', Integer, nullable=False, server_default=text("0")),
    Column('MascotStamp', SmallInteger, nullable=False, server_default=text("0")),
    Column('Coins', Integer, nullable=False, server_default=text("500")),
    Column('Color', Integer, nullable=False, server_default=text("1")),
    Column('Head', SmallInteger, nullable=False, server_default=text("0")),
    Column('Face', SmallInteger, nullable=False, server_default=text("0")),
    Column('Neck', SmallInteger, nullable=False, server_default=text("0")),
    Column('Body', SmallInteger, nullable=False, server_default=text("0")),
    Column('Hand', SmallInteger, nullable=False, server_default=text("0")),
    Column('Feet', SmallInteger, nullable=False, server_default=text("0")),
    Column('Photo', SmallInteger, nullable=False, server_default=text("0")),
    Column('Flag', SmallInteger, nullable=False, server_default=text("0")),
    Column('Permaban', Integer, nullable=False, server_default=text("0")),
    Column('BookModified', Integer, nullable=False, server_default=text("0")),
    Column('BookColor', Integer, nullable=False, server_default=text("1")),
    Column('BookHighlight', Integer, nullable=False, server_default=text("1")),
    Column('BookPattern', Integer, nullable=False, server_default=text("0")),
    Column('BookIcon', Integer, nullable=False, server_default=text("1")),
    Column('AgentStatus', Integer, nullable=False, server_default=text("0")),
    Column('FieldOpStatus', Integer, nullable=False, server_default=text("0")),
    Column('CareerMedals', Integer, nullable=False, server_default=text("0")),
    Column('AgentMedals', Integer, nullable=False, server_default=text("0")),
    Column('LastFieldOp', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('NinjaRank', Integer, nullable=False, server_default=text("0")),
    Column('NinjaProgress', Integer, nullable=False, server_default=text("0")),
    Column('FireNinjaRank', Integer, nullable=False, server_default=text("0")),
    Column('FireNinjaProgress', Integer, nullable=False, server_default=text("0")),
    Column('WaterNinjaRank', Integer, nullable=False, server_default=text("0")),
    Column('WaterNinjaProgress', Integer, nullable=False, server_default=text("0")),
    Column('NinjaMatchesWon', Integer, nullable=False, server_default=text("0")),
    Column('FireMatchesWon', Integer, nullable=False, server_default=text("0")),
    Column('WaterMatchesWon', Integer, nullable=False, server_default=text("0")),
    Column('Rank', Integer, server_default=text("1"))
)


IgnoreList = Table(
    'ignore_list', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('IgnoreID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,nullable=False, index=True)
)


BuddyList = Table(
    'buddy_list', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('BuddyID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, index=True)
)

Inventory = Table(
    'inventory', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('ItemID', SmallInteger, primary_key=True, nullable=False, server_default=text("0"))
)


IglooInventory = Table(
    'igloo_inventory', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, server_default=text("0")),
    Column('IglooID', Integer, primary_key=True, nullable=False, server_default=text("0"))
)


FurnitureInventory = Table(
    'furniture_inventory', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, server_default=text("0")),
    Column('FurnitureID', Integer, primary_key=True, nullable=False, server_default=text("0")),
    Column('Quantity', Integer, nullable=False, server_default=text("1"))
)

class PenguinRowProxy(RowProxyDictionary):

    def __setattr__(self, key, value):
        super(PenguinRowProxy, self).__setattr__(key, value)
        self.engine.execute(Penguin.update(Penguin.c.ID == self.ID).values(**{key: value}))
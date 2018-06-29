# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, text, Table

from Houdini.Data import metadata

Deck = Table(
    'deck', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, index=True),
    Column('CardID', SmallInteger, primary_key=True, nullable=False),
    Column('Quantity', Integer, nullable=False, server_default=text("1"))
)
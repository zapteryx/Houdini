# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text, Table

from Houdini.Data import metadata, RowProxyDictionary

Puffle = Table(
    'puffle', metadata,
    Column('ID', Integer, primary_key=True),
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True),
    Column('Name', String(16), nullable=False),
    Column('AdoptionDate', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('Type', Integer, nullable=False),
    Column('Health', Integer, nullable=False),
    Column('Hunger', Integer, nullable=False),
    Column('Rest', Integer, nullable=False),
    Column('Walking', Integer, server_default=text("0"))
)



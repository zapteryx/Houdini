# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text, Table

from Houdini.Data import metadata

Postcard = Table(
    'postcard', metadata,
    Column('ID', Integer, primary_key=True),
    Column('SenderID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True),
    Column('RecipientID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True),
    Column('Type', SmallInteger, nullable=False),
    Column('SendDate', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('Details', String(255), nullable=False, server_default=text("''")),
    Column('HasRead', Integer, nullable=False, server_default=text("0"))
)
# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text, Table

from Houdini.Data import metadata

Ban = Table(
    'ban', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('Issued', DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()")),
    Column('Expires', DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()")),
    Column('ModeratorID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True),
    Column('Reason', Integer, nullable=False),
    Column('Comment', Text)
)
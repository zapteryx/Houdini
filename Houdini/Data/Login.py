# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text, Table
from Houdini.Data import metadata


Login = Table(
    'login', metadata,
    Column('ID', Integer, primary_key=True),
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True),
    Column('Date', DateTime, nullable=False, server_default=text("current_timestamp()")),
    Column('IPAddress', String(255), nullable=False)
)
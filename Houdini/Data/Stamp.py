# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, text, ForeignKey, Table

from Houdini.Data import metadata


Stamp = Table(
    'stamp', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('Stamp', SmallInteger, primary_key=True, nullable=False),
    Column('Recent', Integer, nullable=False, server_default=text("1"))
)

CoverStamp = Table(
    'cover_stamps', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False),
    Column('Stamp', SmallInteger, primary_key=True, nullable=False, server_default=text("0")),
    Column('X', SmallInteger, nullable=False, server_default=text("0")),
    Column('Y', SmallInteger, nullable=False, server_default=text("0")),
    Column('Type', SmallInteger, nullable=False, server_default=text("0")),
    Column('Rotation', SmallInteger, nullable=False, server_default=text("0")),
    Column('Depth', SmallInteger, nullable=False, server_default=text("0"))
)
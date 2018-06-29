# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Table, text

from Houdini.Data import metadata, RowProxyDictionary

Igloo = Table(
    'igloo', metadata,
    Column('ID', Integer, primary_key=True),
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True, server_default=text("0")),
    Column('Type', SmallInteger, nullable=False, server_default=text("1")),
    Column('Floor', SmallInteger, nullable=False, server_default=text("0")),
    Column('Music', SmallInteger, nullable=False, server_default=text("0")),
    Column('Locked', Integer, nullable=False, server_default=text("0"))
)


IglooFurniture = Table(
    'igloo_furniture', metadata,
    Column('IglooID', ForeignKey(u'igloo.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, index=True),
    Column('FurnitureID', Integer, primary_key=True, nullable=False, server_default=text("1")),
    Column('X', SmallInteger, primary_key=True, nullable=False, server_default=text("0")),
    Column('Y', SmallInteger, primary_key=True, nullable=False, server_default=text("0")),
    Column('Frame', Integer, primary_key=True, nullable=False, server_default=text("0")),
    Column('Rotation', Integer, primary_key=True, nullable=False, server_default=text("0"))
)

class IglooRowProxy(RowProxyDictionary):

    def __setattr__(self, key, value):
        super(IglooRowProxy, self).__setattr__(key, value)
        self.engine.execute(Igloo.update(Igloo.c.ID == self.ID).values(**{key: value}))
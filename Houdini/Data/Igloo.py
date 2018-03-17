# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Table, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata

class Igloo(Base):
    __tablename__ = 'igloo'

    ID = Column(Integer, primary_key=True)
    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True,
                       server_default=text("0"))
    Type = Column(SmallInteger, nullable=False, server_default=text("1"))
    Floor = Column(SmallInteger, nullable=False, server_default=text("0"))
    Music = Column(SmallInteger, nullable=False, server_default=text("0"))
    Locked = Column(Integer, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')


class IglooFurniture(Base):
    __tablename__ = 'igloo_furniture'

    IglooID = Column(ForeignKey(u'igloo.ID'), primary_key=True, nullable=False, index=True)
    FurnitureID = Column(Integer, primary_key=True, nullable=False, server_default=text("1"))
    X = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("0"))
    Y = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("0"))
    Frame = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))
    Rotation = Column(Integer, primary_key=True, nullable=False, server_default=text("0"))

    igloo = relationship(u'Igloo')
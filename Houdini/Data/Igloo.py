# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, text
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
    Location = Column(SmallInteger, nullable=False, server_default=text("0"))
    Locked = Column(SmallInteger, nullable=False, server_default=text("0"))

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


class IglooLike(Base):
    __tablename__ = 'igloo_likes'

    IglooID = Column(ForeignKey(u'igloo.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                     nullable=False)
    OwnerID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    PlayerID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                      nullable=False, index=True)
    Count = Column(Integer, nullable=False)
    Date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    igloo = relationship(u'Igloo')
    penguin = relationship(u'Penguin', primaryjoin='IglooLike.OwnerID == Penguin.ID')
    penguin1 = relationship(u'Penguin', primaryjoin='IglooLike.PlayerID == Penguin.ID')
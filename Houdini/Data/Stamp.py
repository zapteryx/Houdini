# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, text, ForeignKey
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class Stamp(Base):
    __tablename__ = 'stamp'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    Stamp = Column(SmallInteger, primary_key=True, nullable=False)
    Recent = Column(Integer, nullable=False, server_default=text("1"))

    penguin = relationship(u'Penguin')

class CoverStamp(Base):
    __tablename__ = 'cover_stamps'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    Stamp = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("0"))
    X = Column(SmallInteger, nullable=False, server_default=text("0"))
    Y = Column(SmallInteger, nullable=False, server_default=text("0"))
    Type = Column(SmallInteger, nullable=False, server_default=text("0"))
    Rotation = Column(SmallInteger, nullable=False, server_default=text("0"))
    Depth = Column(SmallInteger, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin')
# coding: utf-8
from sqlalchemy import Column, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class GameDataLaunch(Base):
    __tablename__ = 'gamedata_launch'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    LevelID = Column(SmallInteger, nullable=False, primary_key=True)
    PuffleOs = Column(SmallInteger, nullable=False)
    BestTime = Column(SmallInteger, nullable=False)
    TurboDone = Column(SmallInteger, nullable=False)

    penguin = relationship(u'Penguin')

# coding: utf-8
from sqlalchemy import Column, ForeignKey, SmallInteger, text, Time
from sqlalchemy.orm import relationship

from Houdini.Data import Base
from Houdini.Data.Penguin import Penguin

metadata = Base.metadata


class Timer(Base):
    __tablename__ = 'timer'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    TimerActive = Column(SmallInteger, nullable=False, server_default=text("'1'"))
    PlayHourStart = Column(Time, nullable=False)
    PlayHourEnd = Column(Time, nullable=False)
    UTCOffset = Column(SmallInteger, nullable=False)
    TotalDailyTime = Column(SmallInteger, nullable=False, server_default=text("'1440'"))
    MinutesToday = Column(SmallInteger, nullable=False, server_default=text("'0'"))

    penguin = relationship(u'Penguin', primaryjoin='Timer.PenguinID == Penguin.ID')

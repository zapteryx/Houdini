# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base

metadata = Base.metadata


class PlayerReport(Base):
    __tablename__ = 'player_report'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    ReporterID= Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    Reason = Column(SmallInteger, nullable=True)
    Timestamp = Column(DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()"))
    ServerID = Column(SmallInteger, nullable=False)
    RoomID = Column(SmallInteger, nullable=False)

    penguin = relationship(u'Penguin', primaryjoin='PlayerReport.PenguinID == Penguin.ID')

# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base

metadata = Base.metadata


class Ban(Base):
    __tablename__ = 'ban'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    Issued = Column(DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()"))
    Expires = Column(DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()"))
    ModeratorID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    Reason = Column(Integer, nullable=False)
    Comment = Column(Text)

    penguin = relationship(u'Penguin', primaryjoin='Ban.ModeratorID == Penguin.ID')
    penguin1 = relationship(u'Penguin', primaryjoin='Ban.PenguinID == Penguin.ID')
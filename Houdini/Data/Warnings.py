# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base

metadata = Base.metadata


class Warnings(Base):
    __tablename__ = 'warning'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    Issued = Column(DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()"))
    Expires = Column(DateTime, primary_key=True, nullable=False, server_default=text("current_timestamp()"))
    Type = Column(Integer, nullable=False)

    penguin = relationship(u'Penguin', primaryjoin='Warnings.PenguinID == Penguin.ID')

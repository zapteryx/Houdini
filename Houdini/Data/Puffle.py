# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata

class Puffle(Base):
    __tablename__ = 'puffle'

    ID = Column(Integer, primary_key=True)
    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    Name = Column(String(16), nullable=False)
    AdoptionDate = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    Type = Column(Integer, nullable=False)
    Health = Column(Integer, nullable=False)
    Hunger = Column(Integer, nullable=False)
    Rest = Column(Integer, nullable=False)
    Walking = Column(Integer, server_default=text("0"))

    penguin = relationship(u'Penguin')
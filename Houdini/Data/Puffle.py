# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text, SmallInteger
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
    Subtype = Column(Integer, nullable=False)
    Food = Column(Integer, nullable=False)
    Play = Column(Integer, nullable=False)
    Rest = Column(Integer, nullable=False)
    Clean = Column(Integer, nullable=False)
    Walking = Column(Integer, server_default=text("0"))
    Hat = Column(Integer, server_default=text("0"))
    Backyard = Column(Integer, server_default=text("0"))

    penguin = relationship(u'Penguin')

class CareInventory(Base):
    __tablename__ = 'care_inventory'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    ItemID = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("0"))
    Quantity = Column(Integer, nullable=False, server_default=text("1"))

    penguin = relationship(u'Penguin')
# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class Deck(Base):
    __tablename__ = 'deck'

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, index=True)
    CardID = Column(SmallInteger, primary_key=True, nullable=False)
    Quantity = Column(Integer, nullable=False, server_default=text("1"))

    penguin = relationship(u'Penguin')
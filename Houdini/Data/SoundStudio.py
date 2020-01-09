# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from Houdini.Data import Base
from Houdini.Data.Penguin import Penguin
metadata = Base.metadata

class Musics(Base):
    __tablename__ = 'musics'

    ID = Column(Integer, primary_key=True)

    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False)
    Data = Column(String, nullable=False, server_default=text("0"))
    Hash = Column(String, nullable=False, server_default=text("0"))
    Name = Column(String, nullable=False, server_default=text("0"))
    Deleted = Column(SmallInteger, nullable=False, server_default=text("0"))
    Likes = Column(Integer, nullable=False, server_default=text("0"))
    CreatedOn = Column(DateTime, nullable=False, server_default=func.now())
    Sharing = Column(SmallInteger, nullable=False, server_default=text("0"))

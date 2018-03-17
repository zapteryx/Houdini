# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class Postcard(Base):
    __tablename__ = 'postcard'

    ID = Column(Integer, primary_key=True)
    SenderID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=True, index=True)
    RecipientID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    Type = Column(SmallInteger, nullable=False)
    SendDate = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    Details = Column(String(255), nullable=False, server_default=text("''"))
    HasRead = Column(Integer, nullable=False, server_default=text("0"))

    penguin = relationship(u'Penguin', primaryjoin='Postcard.RecipientID == Penguin.ID')
    penguin1 = relationship(u'Penguin', primaryjoin='Postcard.SenderID == Penguin.ID')
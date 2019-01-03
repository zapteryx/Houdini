# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text, Enum
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata

class RedemptionAward(Base):
    __tablename__ = 'redemption_award'

    CodeID = Column(ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                    nullable=False, server_default=text("0"))
    Award = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("1"))

    redemption_code = relationship(u'RedemptionCode')


class RedemptionCode(Base):
    __tablename__ = 'redemption_code'

    ID = Column(Integer, primary_key=True, unique=True)
    Code = Column(String(16), nullable=False, unique=True, server_default=text("''"))
    Type = Column(Enum(u'DS', u'BLANKET', u'CARD', u'GOLDEN', u'CAMPAIGN', u'CATALOG'), nullable=False,
                  server_default=text("'BLANKET'"))
    Coins = Column(Integer, nullable=False, server_default=text("0"))
    Expires = Column(DateTime)

    penguin = relationship(u'Penguin', secondary='penguin_redemption')


class PenguinRedemption(Base):
    __tablename__ = 'penguin_redemption'
    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    CodeID = Column(ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                    nullable=False, index=True, server_default=text("0"))

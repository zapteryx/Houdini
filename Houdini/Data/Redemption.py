# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text, Enum
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata

class RedemptionAward(Base):
    __tablename__ = 'redemption_award'

    CodeID = Column(ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                    nullable=False, server_default=text("0"))
    AwardID = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("1"))
    AwardType = Column(Enum(u'Clothing', u'Furniture', u'Igloo', u'Location', u'Floor', u'Puffle', u'Puffle Item', u'Card'), primary_key=True,
                  nullable=False, server_default=text("'Clothing'"))
    Award = Column(SmallInteger, primary_key=True, nullable=False, server_default=text("1"))

    redemption_code = relationship(u'RedemptionCode')


class RedemptionBook(Base):
    __tablename__ = 'redemption_book'

    BookID = Column(SmallInteger, primary_key=True, nullable=False)
    QuestionID = Column(SmallInteger, primary_key=True, nullable=False)
    Page = Column(SmallInteger, nullable=False)
    Line = Column(SmallInteger, nullable=False)
    WordNumber = Column(SmallInteger, nullable=False)
    Word = Column(String(20), nullable=False)


class RedemptionCode(Base):
    __tablename__ = 'redemption_code'

    ID = Column(Integer, primary_key=True, unique=True)
    Code = Column(String(16), nullable=False, unique=True, server_default=text("''"))
    Type = Column(Enum(u'DS', u'BLANKET', u'CARD', u'GOLDEN', u'CAMPAIGN', u'CATALOG'), nullable=False,
                  server_default=text("'BLANKET'"))
    Coins = Column(Integer, nullable=False, server_default=text("0"))
    SingleUse = Column(SmallInteger, nullable=False, server_default=text("1"))
    Expires = Column(DateTime)

    penguin = relationship(u'Penguin', secondary='penguin_redemption')


class PenguinRedemption(Base):
    __tablename__ = 'penguin_redemption'
    PenguinID = Column(ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, server_default=text("0"))
    CodeID = Column(ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                    nullable=False, index=True, server_default=text("0"))

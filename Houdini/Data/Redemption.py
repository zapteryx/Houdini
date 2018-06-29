# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, text, Table
from sqlalchemy.dialects.mysql.enumerated import ENUM

from Houdini.Data import metadata

RedemptionAward = Table(
    'redemption_award', metadata,
    Column('CodeID', ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, server_default=text("0")),
    Column('Award', SmallInteger, primary_key=True, nullable=False, server_default=text("1"))
)


RedemptionCode = Table(
    'redemption_code', metadata,
    Column('ID', Integer, primary_key=True, unique=True),
    Column('Code', String(16), nullable=False, server_default=text("''")),
    Column('Type', ENUM(u'DS', u'BLANKET', u'CARD', u'GOLDEN', u'CAMPAIGN'), nullable=False, server_default=text("'BLANKET'")),
    Column('Coins', Integer, nullable=False, server_default=text("0")),
    Column('Expires', DateTime)
)


PenguinRedemption = Table(
    'penguin_redemption', metadata,
    Column('PenguinID', ForeignKey(u'penguin.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, server_default=text("0")),
    Column('CodeID', ForeignKey(u'redemption_code.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False, index=True, server_default=text("0"))
)
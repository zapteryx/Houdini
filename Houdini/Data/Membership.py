# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, text
from sqlalchemy.orm import relationship

from Houdini.Data import Base
metadata = Base.metadata


class Membership(Base):
    __tablename__ = 'membership'

    PenguinID = Column(Integer, primary_key=True)
    Status = Column(SmallInteger, nullable=False, server_default=text("0"))
    CurrentPlan = Column(SmallInteger, nullable=False, server_default=text("0"))
    Start = Column(DateTime, nullable=True, server_default=text("current_timestamp()"))
    End = Column(DateTime, nullable=True, server_default=text("current_timestamp()"))
    CumulativeDays = Column(SmallInteger, nullable=False, server_default=text("0"))
    Postcards = Column(SmallInteger, nullable=False, server_default=text("0"))

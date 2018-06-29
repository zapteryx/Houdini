from datetime import datetime

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import RedemptionCode, RedemptionAward, PenguinRedemption

from twisted.internet.defer import inlineCallbacks, returnValue

from sqlalchemy.sql import select

@Handlers.Handle(XT.JoinRedemption)
@Handlers.Throttle(-1)
def handleJoinRedemption(self, data):
    if int(data.ID) != self.user.ID:
        return self.transport.loseConnection()

    if data.LoginKey == "":
        return self.transport.loseConnection()

    if data.LoginKey != self.user.LoginKey:
        self.user.LoginKey = ""
        return self.sendErrorAndDisconnect(101)

    self.sendXt("rjs", "", 1)


@Handlers.Handle(XT.SendCode)
@Handlers.Throttle(2)
@inlineCallbacks
def handleSendCode(self, data):
    code = yield self.engine.first(RedemptionCode.select(RedemptionCode.c.Code == data.Code))

    if code is None:
        returnValue(self.sendError(720))
    redeemed = yield self.engine.scalar(PenguinRedemption.select((PenguinRedemption.c.PenguinID == self.user.ID)
                                                                 & (PenguinRedemption.c.CodeID == code.ID)))
    if redeemed is not None:
        returnValue(self.sendError(721))

    if code.Expires is not None and code.Expires < datetime.now():
        returnValue(self.sendError(726))

    awards = yield self.engine.fetchall(select([RedemptionAward.c.Award]).where(RedemptionAward.c.CodeID == code.ID))
    awardIds = [awardId for awardId, in awards]

    if code.Type == "GOLDEN":
        returnValue(self.sendXt("rsc", "GOLDEN", self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank,
                           int(self.user.FireNinjaRank > 0), int(self.user.WaterNinjaRank > 0)))

    if code.Type == "CARD":
        self.addCards(*awardIds)
    else:
        for itemId in awardIds:
            self.addItem(itemId)

    self.engine.execute(PenguinRedemption.insert(), PenguinID=self.user.ID, CodeID=code.ID)
    self.user.Coins += code.Coins
    self.sendXt("rsc", code.Type, ",".join(map(str, awardIds)), code.Coins)


@Handlers.Handle(XT.SendGoldenChoice)
@Handlers.Throttle(2)
@inlineCallbacks
def handleSendGoldenChoice(self, data):
    awards = yield self.engine.fetchall(select[RedemptionCode.c.Code, RedemptionAward.c.Award].select_from(
        RedemptionCode.join(RedemptionAward, RedemptionAward.c.CodeID == RedemptionCode.c.ID))
                                        .where(RedemptionCode.c.Code == data.Code))

    if awards is None:
        returnValue(self.transport.loseConnection())
    if awards.count() < 6:
        returnValue(self.transport.loseConnection())

    cardIds = [awardId for code, awardId in awards]

    redeemed = yield self.engine.scalar(PenguinRedemption.select(PenguinRedemption.c.CodeID == code.ID))

    if redeemed is not None:
        returnValue(self.transport.loseConnection())

    if data.Choice == 1:
        cardIds = cardIds[:4]
        self.ninjaRankUp()
        self.sendXt("rsgc", ",".join(map(str, cardIds)) + "|" + str(self.user.NinjaRank))
    elif data.Choice == 2:
        self.sendXt("rsgc", ",".join(map(str, cardIds[:4])) + "|" + ",".join(map(str, cardIds[-2:])))
    self.addCards(*cardIds)

    self.engine.execute(PenguinRedemption.insert(), PenguinID=self.user.ID, CodeID=code.ID)
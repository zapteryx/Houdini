from datetime import datetime

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import RedemptionCode, RedemptionAward, PenguinRedemption


@Handlers.Handle(XT.JoinRedemption)
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
def handleSendCode(self, data):
    code = self.session.query(RedemptionCode).filter(RedemptionCode.Code == data.Code).first()

    if code is None:
        return self.sendError(720)

    redeemed = self.session.query(PenguinRedemption).filter_by(PenguinID=self.user.ID, CodeID=code.ID).scalar()
    if redeemed is not None:
        return self.sendError(721)

    if code.Expires is not None and code.Expires < datetime.now():
        return self.sendError(726)

    awards = self.session.query(RedemptionAward.Award).filter_by(CodeID=code.ID)
    awardIds = [awardId for awardId, in awards]

    if code.Type == "GOLDEN":
        return self.sendXt("rsc", "GOLDEN", self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank,
                           int(self.user.FireNinjaRank > 0), int(self.user.WaterNinjaRank > 0))

    if code.Type == "CARD":
        self.addCards(*awardIds)
    else:
        for itemId in awardIds:
            self.addItem(itemId)

    self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=code.ID))
    self.user.Coins += code.Coins
    self.sendXt("rsc", code.Type, ",".join(map(str, awardIds)), code.Coins)


@Handlers.Handle(XT.SendGoldenChoice)
@Handlers.Throttle(2)
def handleSendGoldenChoice(self, data):
    awards = self.session.query(RedemptionCode, RedemptionAward.Award)\
        .join(RedemptionAward, RedemptionAward.CodeID == RedemptionCode.ID)\
        .filter(RedemptionCode.Code == data.Code)

    if awards is None:
        return self.transport.loseConnection()
    if awards.count() < 6:
        return self.transport.loseConnection()

    cardIds = [awardId for code, awardId in awards]

    redeemed = self.session.query(PenguinRedemption).filter_by(CodeID=code.ID).scalar()

    if redeemed is not None:
        return self.transport.loseConnection()

    if data.Choice == 1:
        cardIds = cardIds[:4]
        self.ninjaRankUp()
        self.sendXt("rsgc", ",".join(map(str, cardIds)) + "|" + str(self.user.NinjaRank))
    elif data.Choice == 2:
        self.sendXt("rsgc", ",".join(map(str, cardIds[:4])) + "|" + ",".join(map(str, cardIds[-2:])))
    self.addCards(*cardIds)

    self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=code.ID))
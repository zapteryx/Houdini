from datetime import datetime

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import RedemptionCode, RedemptionAward, PenguinRedemption


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
def handleSendCode(self, data):

    if code is None:
        return self.sendError(720)
    if redeemed is not None:
        return self.sendError(721)

    if code.Expires is not None and code.Expires < datetime.now():
        return self.sendError(726)

    awardIds = [awardId for awardId, in awards]

    if code.Type == "GOLDEN":
        return self.sendXt("rsc", "GOLDEN", self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank,
                           int(self.user.FireNinjaRank > 0), int(self.user.WaterNinjaRank > 0))

    if code.Type == "CARD":
        self.addCards(*awardIds)
    else:
        for itemId in awardIds:
            self.addItem(itemId)

    self.user.Coins += code.Coins
    self.sendXt("rsc", code.Type, ",".join(map(str, awardIds)), code.Coins)


@Handlers.Handle(XT.SendGoldenChoice)
@Handlers.Throttle(2)
def handleSendGoldenChoice(self, data):

    if awards is None:
        return self.transport.loseConnection()
    if awards.count() < 6:
        return self.transport.loseConnection()

    cardIds = [awardId for code, awardId in awards]


    if redeemed is not None:
        return self.transport.loseConnection()

    if data.Choice == 1:
        cardIds = cardIds[:4]
        self.ninjaRankUp()
        self.sendXt("rsgc", ",".join(map(str, cardIds)) + "|" + str(self.user.NinjaRank))
    elif data.Choice == 2:
        self.sendXt("rsgc", ",".join(map(str, cardIds[:4])) + "|" + ",".join(map(str, cardIds[-2:])))
    self.addCards(*cardIds)


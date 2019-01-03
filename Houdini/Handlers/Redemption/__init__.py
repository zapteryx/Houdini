from datetime import datetime

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import RedemptionCode, RedemptionAward, PenguinRedemption
from Houdini.Data.Puffle import Puffle
from Houdini.Handlers.Play.Pet import handleAddInitialCareItems
from Houdini.Handlers.Play.Moderation import cheatBan

treasureBookIds = [14519, 14438, 14523, 11391, 14565, 14650, 14651, 14203, 11165, 14239, 12056, 14562, 16114, 11474, 14707, 16131, 11434, 14151, 14529, 14659, 11882, 15459, 34144, 11883, 34145, 34158, 11254, 13072, 14363, 16071, 10125, 11255, 14364, 16070]

@Handlers.Handle(XT.JoinRedemption)
@Handlers.Throttle(-1)
def handleJoinRedemption(self, data):
    loginArray = data.LoginData.split("|")
    if int(loginArray[0]) != self.user.ID:
        return self.transport.loseConnection()

    if loginArray[3] == "":
        return self.transport.loseConnection()

    if loginArray[3] != self.user.LoginKey:
        self.user.LoginKey = ""
        return self.sendErrorAndDisconnect(101)

    self.user.TBValidation = False
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

    if code.Type == "CATALOG":
        ownedIds = []

        for id in treasureBookIds:
            if id in self.inventory:
                ownedIds.append(id)

        selfRedeemed = self.session.query(PenguinRedemption.CodeID).join(RedemptionCode, RedemptionCode.ID == PenguinRedemption.CodeID) \
                        .filter(RedemptionCode.Type=="CATALOG").filter(PenguinRedemption.PenguinID == self.user.ID).all()
        numRedeemed = len(selfRedeemed)

        # We set this variable so that we don't have to do all the validation again in the other functions
        # If this check fails in the other functions, the player is attempting to perm the items
        self.user.TBValidation = True

        return self.sendXt("rsc", "treasurebook", 1, ",".join(map(str, ownedIds)), numRedeemed)

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

@Handlers.Handle(XT.SendCart)
@Handlers.Throttle(2)
def handleSendCart(self, data):
    if self.user.TBValidation != True:
        return cheatBan(self, self.user.ID, 72, "Attempting to perm Treasure Book")

    if data.Choice is None:
        return self.transport.loseConnection()

    coins = 0

    code = self.session.query(RedemptionCode).filter(RedemptionCode.Code == data.Code).first()
    awards = self.session.query(RedemptionAward.Award).filter_by(CodeID=code.ID)
    awardIds = [str(awardId) for awardId, in awards]

    choices = data.Choice.split(",")
    choices = choices + awardIds

    if "c0" in choices:
        times = choices.count("c0")
        coins = coins + (500*times)
        i = 0
        while (i < times):
            choices.remove("c0")
            i += 1

    for id in choices:
        if id[:1] != "p":
            if int(id) not in treasureBookIds and id not in awardIds:
                return self.transport.loseConnection()
            else:
                self.addItem(id, itemCost=0, sendXt=False)

    coins += code.Coins

    self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=code.ID))
    self.session.commit()

    coins = "" if coins == 0 else coins
    self.sendXt("rscrt", ",".join(choices), coins)
    self.user.TBValidation = False

@Handlers.Handle(XT.RedeemSendPuffle)
@Handlers.Throttle(2)
def handleRedeemSendPuffle(self, data):
    if self.user.TBValidation != True:
        return cheatBan(self, self.user.ID, 72, "Attempting to perm Treasure Book")

    if data.Name is None or data.ID is None:
        return self.transport.loseConnection()

    if data.ID not in range(0,10):
        return self.transport.loseConnection()

    if not 16 > len(data.Name) >= 3:
        self.sendXt("rsp", 0)

    if len(self.puffles) >= 75:
        return self.sendError(440)

    data.TypeId = data.ID
    data.SubtypeId = None
    handleAddInitialCareItems(self, data)

    puffle = Puffle(PenguinID=self.user.ID, Name=data.Name, Type=data.ID,
                    Subtype=0)
    self.session.add(puffle)

    self.receiveSystemPostcard(111, data.Name)
    self.sendXt("rsp", 1)

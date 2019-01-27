from datetime import datetime
import random

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import RedemptionCode, RedemptionAward, PenguinRedemption
from Houdini.Data.Puffle import Puffle
from Houdini.Handlers.Play.Pet import handleAddInitialCareItems
from Houdini.Handlers.Play.Moderation import cheatBan

@Handlers.Handle(XT.SendCode)
@Handlers.Throttle(2)
def handleSendCode(self, data):
    code = self.session.query(RedemptionCode).filter(RedemptionCode.Code == data.Code).first()

    if code is None or code.ID <= 50:
        return self.sendError(720)

    redeemed = self.session.query(PenguinRedemption).filter_by(CodeID=code.ID).all()

    if code.SingleUse == 1:
        if redeemed:
            return self.sendError(721)

    if code.SingleUse == 0:
        for penguin in redeemed:
            if penguin.PenguinID == self.user.ID:
                return self.sendError(721)

    if code.Expires is not None and code.Expires < datetime.now():
        return self.sendError(726)

    if code.Type == "CATALOG":
        ownedIds = []

        for id in self.server.availableClothing["TreasureBook"]:
            if id in self.inventory:
                ownedIds.append(id)

        selfRedeemed = self.session.query(PenguinRedemption.CodeID).join(RedemptionCode, RedemptionCode.ID == PenguinRedemption.CodeID) \
                        .filter(RedemptionCode.Type=="CATALOG").filter(PenguinRedemption.PenguinID == self.user.ID).all()
        numRedeemed = len(selfRedeemed)

        # We set this variable so that we don't have to do all the validation again in the other functions
        # If this check fails in the other functions, the player is attempting to perm the items
        self.user.TBValidation = True

        return self.sendXt("rsc", "treasurebook", 1, ",".join(map(str, ownedIds)), numRedeemed)

    if code.Type == "INNOCENT":
        innocentRedeemed = []

        for id in self.server.availableClothing["Innocent"]:
            if id in self.inventory:
                innocentRedeemed.append(id)
        for id in self.server.availableFurniture["Innocent"]:
            if id in self.furniture:
                innocentRedeemed.append(id)

        innocentFurniture = ["f" + str(item) for item in self.server.availableFurniture["Innocent"]]
        innocentClothing = [str(item) for item in self.server.availableClothing["Innocent"]]
        innocentItems = innocentClothing + innocentFurniture
        awards = []

        while len(awards) < 3:
            if len(innocentRedeemed) >= len(innocentItems):
                # If a player has all 25 items and redeems more codes, give them more furniture
                choice = random.choice(innocentFurniture)
                if choice not in awards:
                    self.addFurniture(int(choice[1:]), sendXt=False)
                    awards.append(choice)
            else:
                choice = random.choice(innocentItems)
                if choice in innocentClothing:
                    if int(choice) not in innocentRedeemed and choice not in awards:
                        self.addItem(int(choice), sendXt=False)
                        awards.append(choice)
                elif choice in innocentFurniture:
                    if int(choice[1:]) not in innocentRedeemed and choice not in awards:
                        self.addFurniture(int(choice[1:]), sendXt=False)
                        awards.append(choice)

        redeemed = len(innocentRedeemed) + 3
        if redeemed == len(innocentItems):
            redeemed += 1
            finalReward = self.server.availableIgloos["Innocent"][0]
            self.addIgloo(finalReward, sendXt=False)
            awards.append("g"+str(finalReward))

        self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=code.ID))
        self.session.commit()

        return self.sendXt("rsc", "INNOCENT", ",".join(map(str, awards)), redeemed, len(innocentItems))

    awards = self.session.query(RedemptionAward).filter_by(CodeID=code.ID).all()
    items = []

    if code.Type == "GOLDEN":
        return self.sendXt("rsc", "GOLDEN", self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank, self.user.SnowNinjaRank,
                           int(self.user.FireNinjaRank > 0), int(self.user.WaterNinjaRank > 0), int(self.user.SnowNinjaRank > 0))

    if code.Type == "CARD":
        cardIds = []

        for award in awards:
            cardIds.append(award.Award)
            items.append(str(award.Award))

        self.addCards(*cardIds)
    else:
        for award in awards:
            if award.AwardType == "Clothing":
                self.addItem(award.Award, sendXt=False)
                items.append(str(award.Award))
            elif award.AwardType == "Furniture":
                self.addFurniture(award.Award, sendXt=False)
                items.append("f" + str(award.Award))
            elif award.AwardType == "Igloo":
                self.addIgloo(award.Award, sendXt=False)
                items.append("g" + str(award.Award))
            elif award.AwardType == "Location":
                self.addLocation(award.Award, sendXt=False)
                items.append("loc" + str(award.Award))
            elif award.AwardType == "Floor":
                self.addFlooring(award.Award, sendXt=False)
                items.append("flr" + str(award.Award))
            elif award.AwardType == "Puffle":
                items.append("p" + str(award.Award))
                self.user.isRedeemingPuffle = True
            elif award.AwardType == "Puffle Item":
                self.addCareItem(award.Award, sendXt=False)
                items.append("pi" + str(award.Award))

    self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=code.ID))

    self.user.Coins += code.Coins
    coins = "" if code.Coins == 0 else code.Coins

    self.session.commit()
    self.sendXt("rsc", code.Type, ",".join(items), coins)

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
            if int(id) not in self.server.availableClothing["TreasureBook"] and id not in awardIds:
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
    if self.user.TBValidation != True and self.user.isRedeemingPuffle != True:
        return cheatBan(self, self.user.ID, 72, "Attempting to perm Puffle")

    if data.Name is None or data.ID is None:
        return self.transport.loseConnection()

    if data.ID not in self.server.puffles:
        return self.transport.loseConnection()

    typeId = self.server.puffles.getParentId(data.ID)
    if typeId == data.ID:
        data.TypeId = data.ID
        data.SubtypeId = 0
    else:
        data.TypeId = typeId
        data.SubtypeId = data.ID

    if not 16 > len(data.Name) >= 3:
        self.sendXt("rsp", 0)

    if len(self.puffles) >= 75 and self.user.Moderator == 0:
        return self.sendError(440)

    handleAddInitialCareItems(self, data)

    puffle = Puffle(PenguinID=self.user.ID, Name=data.Name, Type=data.TypeId,
                    Subtype=data.SubtypeId)
    self.session.add(puffle)

    self.receiveSystemPostcard(111, data.Name)
    self.sendXt("rsp", 1)
    self.user.isRedeemingPuffle = False

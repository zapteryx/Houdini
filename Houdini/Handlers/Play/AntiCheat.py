from sqlalchemy import and_

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Play.Moderation import cheatBan
from Houdini.Data.Redemption import RedemptionAward, RedemptionCode, PenguinRedemption

def runAntiCheat(self):
    if self.user.Moderator == 0:
        self.antiCheatInnocentItems = False
        self.antiCheatEPFItems = False
        if antiCheatItems(self) is not None:
            return True
        if antiCheatFurniture(self) is not None:
            return True
        if antiCheatIgloos(self) is not None:
            return True
        if self.antiCheatInnocentItems:
            if antiCheatInnocent(self) is not None:
                return True
        if self.antiCheatEPFItems:
            if antiCheatEPF(self) is not None:
                return True
        if antiCheatLocations(self) is not None:
            return True
        if antiCheatFloors(self) is not None:
            return True
        if antiCheatCareItems(self) is not None:
            return True

def antiCheatItems(self):
    if self.user.Moderator == 0:
        for item in self.inventory:
            if item in self.server.availableClothing["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Clothing")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable item {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable item {} permed".format(str(item)))
                    return True

            elif item in self.server.availableClothing["Ninja"]["CardJitsu"]:
                ninjaItems = self.server.availableClothing["Ninja"]["CardJitsu"]
                ninjaRank = self.user.NinjaRank
                rankNeeded = ninjaItems.index(item) + 1

                if ninjaRank < rankNeeded:
                    self.logger.info("Ninja item {} detected in inventory of user {} without sufficient rank".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Ninja item {} permed".format(str(item)))
                    return True

            elif item in self.server.availableClothing["Ninja"]["CardFire"]:
                fireItems = self.server.availableClothing["Ninja"]["CardFire"]
                fireRank = self.user.FireNinjaRank
                rankNeeded = fireItems.index(item) + 1

                if fireRank < rankNeeded:
                    self.logger.info("Fire ninja item {} detected in inventory of user {} without sufficient rank".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Fire ninja item {} permed".format(str(item)))
                    return True
            elif item in self.server.availableClothing["Innocent"]:
                self.antiCheatInnocentItems = True
            elif item in self.server.availableClothing["EliteGear"]:
                self.antiCheatEPFItems = True
            elif self.server.items.isBait(item):
                if not self.server.items.isItemEPF(item):
                    self.logger.info("Bait item {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Bait item {} permed".format(str(item)))
                    return True

def antiCheatFurniture(self):
    if self.user.Moderator == 0:
        for item in self.furniture:
            if item in self.server.availableFurniture["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Furniture")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable furniture {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable furniture {} permed".format(str(item)))
                    return True

            elif item in self.server.availableFurniture["Innocent"]:
                self.antiCheatInnocentItems = True
            elif self.server.furniture.isBait(item):
                self.logger.info("Bait furniture {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Bait furniture {} permed".format(str(item)))
                return True

def antiCheatIgloos(self):
    if self.user.Moderator == 0:
        for item in self.iglooInventory:
            if item in self.server.availableIgloos["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Igloo")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable igloo {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable igloo {} permed".format(str(item)))
                    return True

            elif item in self.server.availableIgloos["Innocent"]:
                self.antiCheatInnocentItems = True
            elif self.server.igloos.isBait(item):
                self.logger.info("Bait igloo {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Bait furniture {} permed".format(str(item)))
                return True

def antiCheatLocations(self):
    if self.user.Moderator == 0:
        for item in self.locations:
            if item in self.server.availableLocations["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Location")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable location {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable location {} permed".format(str(item)))
                    return True

            elif self.server.locations.isBait(item):
                self.logger.info("Bait location {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Bait location {} permed".format(str(item)))
                return True

def antiCheatFloors(self):
    if self.user.Moderator == 0:
        for item in self.floors:
            if item in self.server.availableFlooring["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Floor")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable floor {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable floor {} permed".format(str(item)))
                    return True

            elif self.server.floors.isBait(item):
                self.logger.info("Bait floor {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Bait floor {} permed".format(str(item)))
                return True

def antiCheatCareItems(self):
    if self.user.Moderator == 0:
        for item in self.careInventory:
            if item in self.server.availableCareItems["Unlockable"]:
                awards = self.session.query(RedemptionAward).filter(and_(RedemptionAward.Award == item, RedemptionAward.AwardType == "Puffle Item")).all()
                for award in awards:
                    selfRedeemed = self.session.query(PenguinRedemption.CodeID) \
                        .filter(and_(PenguinRedemption.CodeID == award.CodeID,PenguinRedemption.PenguinID == self.user.ID)) \
                        .scalar()
                    if selfRedeemed:
                        break
                else:
                    self.logger.info("Unlockable care item {} detected in inventory of user {} when no code entered".format(str(item), str(self.user.ID)))
                    cheatBan(self, self.user.ID, 72, "Unlockable care item {} permed".format(str(item)))
                    return True

            elif self.server.careItems.isBait(item):
                self.logger.info("Bait care item {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Bait care item {} permed".format(str(item)))
                return True

def antiCheatInnocent(self):
    if self.user.Moderator == 0:
        innocentRedeemed = self.session.query(PenguinRedemption.CodeID) \
                .join(RedemptionCode, RedemptionCode.ID == PenguinRedemption.CodeID) \
                .filter(RedemptionCode.Type=="INNOCENT") \
                .filter(PenguinRedemption.PenguinID == self.user.ID).all()

        if len(innocentRedeemed) < 8:
            if self.server.availableIgloos["Innocent"][0] in self.iglooInventory:
                self.logger.info("Innocent bonus igloo {} detected in inventory of user {} without sufficient codes".format(str(item), str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Innocent bonus igloo {} permed".format(str(item)))
                return True

            innocentClothing = 0
            innocentFurniture = 0
            for item in self.server.availableClothing["Innocent"]:
                if item in self.inventory:
                    innocentClothing += 1
            for item in self.server.availableFurniture["Innocent"]:
                if item in self.furniture:
                    innocentFurniture += 1
            innocentItems = (innocentClothing + innocentFurniture)
            if (float(innocentItems) / len(innocentRedeemed)) > 3:
                self.logger.info("Innocent items detected in inventory of user {} without sufficient codes".format(str(self.user.ID)))
                cheatBan(self, self.user.ID, 72, "Innocent items permed")
                return True

def antiCheatEPF(self):
    if self.user.Moderator == 0:
        totalCost = 0
        for item in self.server.availableClothing["EliteGear"]:
            if item in self.inventory:
                itemCost = self.server.items.getCost(item)
                totalCost += itemCost

        totalMedals = self.user.CareerMedals
        if totalMedals < totalCost:
            self.logger.info("Elite gear detected in inventory of user {} without sufficient medals".format(str(self.user.ID)))
            cheatBan(self, self.user.ID, 72, "Elite gear permed")
            return True

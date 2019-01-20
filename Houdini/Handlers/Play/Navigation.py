import time, random
from sqlalchemy import and_

from Houdini.Handlers import Handlers, XT
from Houdini.Crumbs.Room import Room
from Houdini.Handlers.Play.Buddy import handleRefreshPlayerFriendInfo
from Houdini.Handlers.Play.Pet import handleGetMyPlayerPuffles
from Houdini.Handlers.Play.Stampbook import getStampsString
from Houdini.Data.Penguin import Penguin, BuddyList
from Houdini.Data.Redemption import RedemptionAward, PenguinRedemption
from Houdini.Data.Timer import Timer
from Houdini.Handlers.Play.Timer import updateEggTimer, checkHours
from Houdini.Handlers.Play.Moderation import cheatBan

RoomFieldKeywords = {
    "Id": None,
    "InternalId": None,
    "Key": "Igloo",
    "Name": "Igloo",
    "DisplayName": "Igloo",
    "MusicId": 0,
    "Member": 0,
    "Path": "",
    "MaxUsers": 100,
    "RequiredItem": None,
    "ShortName": "Igloo"
}

@Handlers.Handle(XT.JoinWorld)
@Handlers.Throttle(-1)
def handleJoinWorld(self, data):
    if int(data.ID) != self.user.ID:
        return self.transport.loseConnection()

    if data.LoginKey == "":
        return self.transport.loseConnection()

    if data.LoginKey != self.user.LoginKey:
        self.user.LoginKey = ""
        return self.sendErrorAndDisconnect(101)

    if not self.user.Approval:
        # Set the player's nickname to their ID if their name isn't approved
        # This prevents even the player from seeing their own name underneath their ID in-game
        self.user.Nickname = "P" + str(self.user.ID)

    self.server.players[self.user.ID] = self
    self.user.LoginKey = ""

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable item {} permed".format(str(item)))

            elif item in self.server.availableClothing["Innocent"]:
                # TODO: Support checking if a player obtained Innocent items legitimately
                break
            elif self.server.items.isBait(item):
                if not self.server.items.isItemEPF(item):
                    # TODO: Support checking if a player obtained EPF items legitimately
                    self.logger.info("Bait item {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                    return cheatBan(self, self.user.ID, 72, "Bait item {} permed".format(str(item)))

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable furniture {} permed".format(str(item)))

            elif item in self.server.availableFurniture["Innocent"]:
                # TODO: Support checking if a player obtained Innocent items legitimately
                break
            elif self.server.furniture.isBait(item):
                self.logger.info("Bait furniture {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                return cheatBan(self, self.user.ID, 72, "Bait furniture {} permed".format(str(item)))

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable igloo {} permed".format(str(item)))

            elif item in self.server.availableIgloos["Innocent"]:
                # TODO: Support checking if a player obtained Innocent items legitimately
                break
            elif self.server.igloos.isBait(item):
                self.logger.info("Bait igloo {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                return cheatBan(self, self.user.ID, 72, "Bait furniture {} permed".format(str(item)))

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable location {} permed".format(str(item)))

            elif self.server.locations.isBait(item):
                self.logger.info("Bait location {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                return cheatBan(self, self.user.ID, 72, "Bait location {} permed".format(str(item)))

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable floor {} permed".format(str(item)))

            elif self.server.floors.isBait(item):
                self.logger.info("Bait floor {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                return cheatBan(self, self.user.ID, 72, "Bait floor {} permed".format(str(item)))

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
                    return cheatBan(self, self.user.ID, 72, "Unlockable care item {} permed".format(str(item)))

            elif self.server.careItems.isBait(item):
                self.logger.info("Bait care item {} detected in inventory of user {}".format(str(item), str(self.user.ID)))
                return cheatBan(self, self.user.ID, 72, "Bait care item {} permed".format(str(item)))

    timer = self.session.query(Timer).filter(Timer.PenguinID == self.user.ID).first()

    if timer is not None and timer.TimerActive == 1:
        if timer.TotalDailyTime != 0:
            timeLeft = timer.TotalDailyTime - timer.MinutesToday
            if timer.MinutesToday >= timer.TotalDailyTime:
                return self.sendErrorAndDisconnect(910)
            else:
                updateEggTimer(self, timeLeft + 1, timer.TotalDailyTime)
        else:
            timeLeft = 1440

        if str(timer.PlayHourStart) != "00:00:00" and str(timer.PlayHourEnd) != "23:59:59":
            checkHours(self, timer.PlayHourStart, timer.PlayHourEnd, 1)
    else:
        timeLeft = 1440

    self.sendXt("activefeatures")

    self.sendXt("js", self.user.AgentStatus, 0, self.user.Moderator, self.user.BookModified)

    currentTime = int(time.time())
    penguinStandardTime = currentTime * 1000
    serverTimeOffset = 8

    self.sendXt("lp", self.getPlayerString(), self.user.Coins, self.user.SafeChat, timeLeft,
                penguinStandardTime, self.age, 0, self.user.MinutesPlayed, self.user.MembershipLeft, serverTimeOffset, 1, 0, 211843)

    handleRefreshPlayerFriendInfo(self, data)

    handleGetMyPlayerPuffles(self, [])

    self.sendXt("gps", self.user.ID, getStampsString(self, self.user.ID))

    self.inBackyard = False

    if self.user.ID in self.server.mascots:
        for playerId in self.server.players.keys():
            player = self.server.players[playerId]
            if self.user.ID in player.characterBuddies:
                player.sendXt("cron", self.user.ID)
    else:
        for buddyId, buddyNickname in self.buddies.items():
            if buddyId in self.server.players:
                self.server.players[buddyId].sendXt("bon", self.user.ID)
        for characterId in self.characterBuddies:
            if characterId in self.server.players:
                self.sendXt("cron", characterId)

    self.server.rooms[100].add(self)

@Handlers.Handle(XT.JoinRoom)
@Handlers.Throttle(0.2)
def handleJoinRoom(self, data):
    tableRooms = (111, 220, 221, 422)
    if data.RoomId in tableRooms:
        self.sendXt("jr", data.RoomId)

    room = self.server.rooms[data.RoomId]

    if len(room.players) >= room.MaxUsers:
        return self.sendError(210)

    if data.RoomId in self.server.rooms:
        self.x = data.X
        self.y = data.Y
        self.frame = 1

        self.room.remove(self)
        room.add(self)

@Handlers.Handle(XT.RefreshRoom)
def handleRefreshRoom(self, data):
    self.room.refresh(self)

@Handlers.Handle(XT.JoinPlayerIgloo)
@Handlers.Throttle()
def handleJoinPlayerIgloo(self, data):
    if data.Id != self.user.ID and data.Id not in self.buddies \
            and data.Id not in self.server.openIgloos:
        return self.transport.loseConnection()

    data.Id += 1000

    if data.Id not in self.server.rooms:
        iglooFieldKeywords = RoomFieldKeywords.copy()
        iglooFieldKeywords["Id"] = data.Id
        iglooFieldKeywords["InternalId"] = data.Id - 1000
        iglooFieldKeywords["IglooId"] = self.session.query(Penguin.Igloo).filter_by(ID=data.Id - 1000).scalar()

        igloo = self.server.rooms[data.Id] = Room(**iglooFieldKeywords)
    else:
        igloo = self.server.rooms[data.Id]

    if len(igloo.players) >= igloo.MaxUsers:
        return self.sendError(210)

    self.room.remove(self)

    if data.RoomType == "backyard":
        self.inBackyard = True
    else:
        self.inBackyard = False

    igloo.add(self, data.RoomType)

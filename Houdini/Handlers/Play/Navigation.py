import time, random
from datetime import date

from Houdini.Handlers import Handlers, XT
from Houdini.Crumbs.Room import Room

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
    "JumpEnabled": False,
    "JumpDisabled": True,
    "RequiredItem": None,
    "ShortName": "Igloo"
}

@Handlers.Handle(XT.JoinWorld)
def handleJoinWorld(self, data):
    if int(data.ID) != self.user.ID:
        return self.transport.loseConnection()

    if data.LoginKey == "":
        return self.transport.loseConnection()

    if data.LoginKey != self.user.LoginKey:
        self.user.LoginKey = ""
        return self.sendErrorAndDisconnect(101)

    hasUpdatedBookCover = int(self.user.StampBook != "1%1%0%1")
    self.sendXt("js", 1, self.agentStatus, self.user.Moderator, hasUpdatedBookCover)

    # Casting to integer floor's and removes the decimal
    currentTime = int(time.time())
    penguinStandardTime = currentTime * 1000
    serverTimeOffset = 7

    registrationDate = date.fromtimestamp(self.user.RegistrationDate)
    currentDateTime = date.fromtimestamp(currentTime)

    self.age = (currentDateTime - registrationDate).days

    for furnitureDetails in self.user.Furniture.split("%"):
        if not furnitureDetails:
            break
        furnitureId, furnitureQuantity = furnitureDetails.split("|")
        self.furniture[int(furnitureId)] = int(furnitureQuantity)

    self.sendXt("lp", self.getPlayerString(), self.user.Coins, 0, 1440,
                penguinStandardTime, self.age, 0, self.age, None, serverTimeOffset)

    self.sendXt("gps", self.user.ID, self.user.Stamps)

    self.user.LoginKey = ""
    self.user.LastLogin = currentTime

    self.session.commit()

    self.server.players[self.user.ID] = self

    buddyList = self.getBuddyList()

    for buddyId in buddyList.keys():
        if buddyId in self.server.players:
            self.server.players[buddyId].sendXt("bon", self.user.ID)

    randomRoomId = random.choice(self.server.spawnRooms)
    self.server.rooms[randomRoomId].add(self)

@Handlers.Handle(XT.JoinRoom)
def handleJoinRoom(self, data):
    if data.RoomId in self.server.rooms:
        self.x = data.X
        self.y = data.Y
        self.frame = 1

        self.room.remove(self)
        self.server.rooms[data.RoomId].add(self)

@Handlers.Handle(XT.RefreshRoom)
def handleRefreshRoom(self, data):
    self.room.refresh(self)

@Handlers.Handle(XT.JoinPlayerIgloo)
def handleJoinPlayerIgloo(self, data):
    if data.Id < 1000:
        return self.transport.loseConnection()

    playerId = data.Id - 1000

    if playerId != self.user.ID and playerId not in self.buddies \
            and playerId not in self.server.openIgloos:
        return self.transport.loseConnection()

    if data.Id not in self.server.rooms:
        iglooFieldKeywords = RoomFieldKeywords.copy()
        iglooFieldKeywords["Id"] = data.Id
        iglooFieldKeywords["InternalId"] = data.Id

        igloo = self.server.rooms[data.Id] = Room(**iglooFieldKeywords)
    else:
        igloo = self.server.rooms[data.Id]

    self.room.remove(self)

    self.sendXt("jp", data.Id)
    igloo.add(self)
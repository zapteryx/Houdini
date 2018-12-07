import time, random

from Houdini.Handlers import Handlers, XT
from Houdini.Crumbs.Room import Room
from Houdini.Handlers.Play.Pet import handleGetMyPlayerPuffles
from Houdini.Handlers.Play.Stampbook import getStampsString
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Timer import Timer
from Houdini.Handlers.Play.Timer import updateEggTimer, checkHours

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

    self.sendXt("activefeatures")

    self.sendXt("js", self.user.AgentStatus, 0, self.user.Moderator, self.user.BookModified)

    handleGetMyPlayerPuffles(self, [])

    currentTime = int(time.time())
    penguinStandardTime = currentTime * 1000
    serverTimeOffset = 8

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

    self.sendXt("lp", self.getPlayerString(), self.user.Coins, self.user.SafeChat, timeLeft,
                penguinStandardTime, self.age, 0, self.user.MinutesPlayed, None, serverTimeOffset, 1, 0, 211843)

    self.sendXt("gps", self.user.ID, getStampsString(self, self.user.ID))

    self.user.LoginKey = ""

    self.server.players[self.user.ID] = self

    for buddyId, buddyNickname in self.buddies.items():
        if buddyId in self.server.players:
            self.server.players[buddyId].sendXt("bon", self.user.ID)

    randomRoomId = 100
    self.server.rooms[randomRoomId].add(self)

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

    igloo.add(self, data.RoomType)

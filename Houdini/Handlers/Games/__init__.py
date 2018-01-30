import math, time

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Play.Moderation import cheatBan
from Houdini.Handlers.Games.Table import Table
from Houdini.Handlers.Games.FindFour import FindFour
from Houdini.Handlers.Games.Mancala import Mancala
from Houdini.Handlers.Games.TreasureHunt import TreasureHunt
from Houdini.Handlers.Games.Waddle import Waddle
from Houdini.Handlers.Games.SledRace import SledRace
from Houdini.Handlers.Games.CardJitsu import CardMat

maxCoins = 1000000

maxScorePerMinute = {
    901: 2000,
    902: 2000,
    903: 500,
    905: 2500
}

def determineCoinsEarned(gameId, gameScore):
    defaultScoreGames = (904, 905, 906, 912, 916, 917, 918, 919, 950)

    if gameId in defaultScoreGames:
        coinsEarned = gameScore
    else:
        coinsEarned = math.ceil(gameScore / 10)

    return coinsEarned

def determineCoinsOverdose(self, score):
    maxGameScore = maxScorePerMinute[self.room.Id] if self.room.Id in maxScorePerMinute else 9000
    minutesSinceJoin = ((int(time.time()) - self.lastJoinedRoom) / 60) + 1
    maxGameScore = maxGameScore * minutesSinceJoin
    self.logger.info("%d: User earned %d score in %d minutes, that's %d points per minute", self.room.Id, score,
                     minutesSinceJoin, score / minutesSinceJoin)
    if score > maxGameScore:
        self.logger.info("User tried to get %d score in %d minutes! Max is %d", score, minutesSinceJoin,
                         maxGameScore)
        return True
    return False

@Handlers.Handle(XT.GameOver)
def handleSendGameOver(self, data):
    if self.waddle or self.table:
        return

    if self.room.isGame:
        if determineCoinsOverdose(self, data.Score):
            return cheatBan(self, self.user.ID, comment="Coin cheat detected")

        if self.server.stampGroups.isStampRoom(self.room.Id):
            roomStamps = self.server.stampGroups.getStampGroupByRoomId(self.room.Id).StampsById
            myStamps = map(int, self.user.Stamps.split("|")) if self.user.Stamps else []
            collectedStamps = []
            totalGameStamps = 0

            for myStamp in myStamps:
                if myStamp in roomStamps:
                    collectedStamps.append(myStamp)

                for groupId, stampGroup in self.server.stampGroups.schemaObjects.items():
                    if myStamp in stampGroup.StampsById:
                        totalGameStamps += 1

            collectedStamps = [str(myStamp) for myStamp in myStamps if myStamp in roomStamps]
            totalStamps = len(collectedStamps)
            totalStampsGame = len(roomStamps)
            collectedStampsString = "|".join(collectedStamps)

            if totalStamps == totalStampsGame:
                data.Score *= 2

            coinsEarned = determineCoinsEarned(self.room.Id, data.Score)

            self.user.Coins = max(0, min(self.user.Coins + coinsEarned, maxCoins))
            self.sendXt("zo", self.user.Coins, collectedStampsString, totalStamps, totalStampsGame, totalGameStamps)
        else:
            coinsEarned = determineCoinsEarned(self.room.Id, data.Score)

            self.user.Coins = max(0, min(self.user.Coins + coinsEarned, maxCoins))
            self.sendXt("zo", self.user.Coins, "", 0, 0, 0)

@Handlers.Handle(XT.MovePuck)
def handleMovePuck(self, data):
    if self.room.Id == 802: # Or disconnect if it isn't the ice rink :shrug:
        self.server.rinkPuck = (data.X, data.Y)

        self.room.sendXt("zm", self.user.ID, data.X, data.Y, data.SpeedX, data.SpeedY)

@Handlers.Handle(XT.GetGame)
def handleGetGame(self, data):
    if self.room.Id == 802:
        puckX, puckY = self.server.rinkPuck if hasattr(self.server, "rinkPuck") else (0, 0)
        self.sendXt("gz", puckX, puckY)

def createTables(tablesConfig, roomObjects):
    tableTypes = [("Four", FindFour), ("Mancala", Mancala),
                  ("Treasure", TreasureHunt)]

    for tableType in tableTypes:
        typeKey, typeClass = tableType
        tableRooms = tablesConfig[typeKey]

        for room in tableRooms:
            roomObject = roomObjects[room["RoomId"]]
            tableIds = room["Tables"]

            for tableId in tableIds:
                tableObject = Table(tableId, typeClass, roomObject)
                roomObject.tables[tableId] = tableObject

def createWaddles(waddlesConfig, roomObjects):
    waddleTypes = [("Sled", SledRace), ("Card", CardMat)]

    for waddleType in waddleTypes:
        typeKey, typeClass = waddleType
        waddleRooms = waddlesConfig[typeKey]

        for room in waddleRooms:
            roomObject = roomObjects[room["RoomId"]]
            waddles = room["Waddles"]

            for waddle in waddles:
                waddleObject = Waddle(waddle["Id"], waddle["Seats"],
                                      typeClass, roomObject)
                roomObject.waddles[waddle["Id"]] = waddleObject
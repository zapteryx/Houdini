import math
from Houdini.Handlers import Handlers, XT

def determineCoinsEarned(gameId, gameScore):
    defaultScoreGames = (904, 905, 906, 912, 916, 917, 918, 919, 950)

    if gameId in defaultScoreGames:
        coinsEarned = gameScore
    else:
        coinsEarned = math.ceil(gameScore / 10)

    return coinsEarned

@Handlers.Handle(XT.GameOver)
def handleSendGameOver(self, data):
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
        self.user.Coins += coinsEarned
        self.sendXt("zo", self.user.Coins, collectedStampsString, totalStamps, totalStampsGame, totalGameStamps)

    else:
        coinsEarned = determineCoinsEarned(self.room.Id, data.Score)
        self.user.Coins += coinsEarned
        self.sendXt("zo", self.user.Coins, "", 0, 0, 0)
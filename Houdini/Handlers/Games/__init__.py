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
    if self.room.externalId in self.server.stamps:
        myStamps = map(int, self.user.Stamps.split("|")) if self.user.Stamps else []
        collectedStamps = []
        totalGameStamps = 0

        for myStamp in myStamps:
            if myStamp in self.server.stamps[self.room.externalId]:
                collectedStamps.append(myStamp)

            for roomStamps in self.server.stamps.values():
                if myStamp in roomStamps:
                    totalGameStamps += 1

        collectedStamps = [str(myStamp) for myStamp in myStamps if myStamp in self.server.stamps[self.room.externalId]]
        totalStamps = len(collectedStamps)
        totalStampsGame = len(self.server.stamps[self.room.externalId])
        collectedStampsString = "|".join(collectedStamps)

        if totalStamps == totalStampsGame:
            data.Score *= 2

        coinsEarned = determineCoinsEarned(self.room.externalId, data.Score)
        self.user.Coins += coinsEarned
        self.sendXt("zo", self.user.Coins, collectedStampsString, totalStamps, totalStampsGame, totalGameStamps)

    else:
        coinsEarned = determineCoinsEarned(self.room.externalId, data.Score)
        self.user.Coins += coinsEarned
        self.sendXt("zo", self.user.Coins, "", 0, 0, 0)
import random

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.Table import TableHandler

class TreasureHunt(object):

    def __init__(self):
        self.mapWidth = 10
        self.mapHeight = 10
        self.coinNumHidden = 0
        self.gemNumHidden = 0
        self.turns = 12
        self.gemValue = 25
        self.coinValue = 1
        self.gemLocations = []
        self.treasureMap = []
        self.totalCoinsFound = 0
        self.totalGemsFound = 0
        self.emeraldFound = 0
        self.digRecordNames = []
        self.digRecordDirections = []
        self.digRecordNumbers = []
        self.emerald = 0
        self.currentPlayer = 1
        self.generateMap()

    def generateMap(self):
        for row in range(self.mapHeight):
            self.treasureMap.append([])
            for column in range(self.mapWidth):
                self.treasureMap[row].append([self.generateTreasure(row, column), 0])

    def isValidMove(self, movie, direction, spade):
        testMovie = direction + "button" + str(spade) + "_mc"
        if testMovie == movie and direction in ["down", "right"] and 0 <= spade <= 9:
            if direction == "right":
                row = self.treasureMap[spade]
                for column, tiles in enumerate(row):
                    treasure, digs = self.treasureMap[spade][column]
                    if digs == 2:
                        return False
            elif direction == "down":
                for row, columns in enumerate(self.treasureMap):
                    treasure, digs = self.treasureMap[row][spade]
                    if digs == 2:
                        return False
            return True
        return False

    def makeMove(self, movie, direction, spade):
        if direction == "right":
            row = self.treasureMap[spade]
            for column, tiles in enumerate(row):
                self.dig(spade, column)
        elif direction == "down":
            for row, columns in enumerate(self.treasureMap):
                self.dig(row, spade)

        self.turns -= 1
        self.digRecordNames.append(movie)
        self.digRecordDirections.append(direction)
        self.digRecordNumbers.append(spade)

    def isGemUncovered(self, row, column):
        for deltaRow, deltaColumn in [(0, 1), (1, 1), (1, 0)]:
            treasure, digs = self.treasureMap[row + deltaRow][column + deltaColumn]
            if digs != 2:
                return False
        return True

    def getGemByPiece(self, row, column):
        for deltaRow, deltaColumn in [(0, -1), (-1, -1), (-1, 0)]:
            if row > 0 and column > 0:
                treasure, digs = self.treasureMap[row + deltaRow][column + deltaColumn]
                if treasure == 2 or treasure == 4:
                    return row + deltaRow, column + deltaColumn
        return False

    def dig(self, row, column):
        self.treasureMap[row][column][1] += 1
        treasure, digs = self.treasureMap[row][column]
        if digs == 2:
            if treasure == 1:
                self.totalCoinsFound += 1
            elif treasure == 2 or treasure == 4:
                if not self.isGemUncovered(row, column):
                    return
                self.totalGemsFound += 1
            elif treasure == 3:
                treasureRow, treasureColumn = self.getGemByPiece(row, column)
                if not self.isGemUncovered(treasureRow, treasureColumn):
                    return
                self.totalGemsFound += 1
                if treasure == 4:
                    self.emeraldFound = 1

    def generateTreasure(self, row, column):
        treasureType = [
            ("None", 0, 60), ("Coin", 1, 40), ("Gem", 2, 1), ("Emerald", 4, 0.5)
        ]

        if self.getGemByPiece(row, column):
            return 3

        if row + 1 == self.mapHeight or column + 1 == self.mapWidth:
            treasureType = treasureType[:2]

        total = sum(weight for name, value, weight in treasureType)
        r, i = random.uniform(0, total), 0

        for name, value, weight in treasureType:
            if i + weight >= r:
                self.coinNumHidden = self.coinNumHidden + 1 if value == 1 else self.coinNumHidden

                if value > 1:
                    self.gemNumHidden += 1
                    self.gemLocations.append(str(row) + "," + str(column))

                if self.emerald:
                    return 2
                if value == 4 and not self.emerald:
                    self.emerald = 1

                return value
            i += weight

    def getString(self):
        treasureMap = ",".join(str(item) for row in self.treasureMap for item, digs in row)
        gemLocations = ",".join(self.gemLocations)
        gameArray = [self.mapWidth, self.mapHeight, self.coinNumHidden, self.gemNumHidden, self.turns,
                     self.gemValue, self.coinValue, gemLocations, treasureMap]
        if self.digRecordNumbers:
            gameArray += [self.totalCoinsFound, self.totalGemsFound, self.emeraldFound]
            gameArray += [",".join(self.digRecordNames), ",".join(self.digRecordDirections),
                          ",".join(map(str, self.digRecordNumbers))]
        return "%".join(map(str, gameArray))

    def determineWinnings(self):
        total = self.totalCoinsFound * self.coinValue
        total += self.totalGemsFound * self.gemValue
        total += self.emeraldFound * self.gemValue * 3
        return total

@Handlers.Handle(XT.GetGame)
@TableHandler(TreasureHunt)
def handleGetGame(self, data):
    if len(self.table.penguins) == 2:
        playerOne, playerTwo = self.table.penguins[:2]
        self.sendXt("gz", playerOne.user.Nickname, str())
        return
    self.sendXt("gz", self.table.getString())

@Handlers.Handle(XT.JoinGame)
@TableHandler(TreasureHunt)
def handleJoinGame(self, data):
    gameFull = len(self.table.penguins) > 2
    if not gameFull:
        seatId = self.table.getSeatId(self)
        self.sendXt("jz", seatId)
        self.table.sendXt("uz", seatId, self.user.Nickname)

        if len(self.table.penguins) == 2:
            self.table.sendXt("sz", self.table.getString())

@Handlers.Handle(XT.SendMove)
@TableHandler(TreasureHunt)
def handleSendMove(self, data):
    try:
        seatId = self.table.getSeatId(self)
        isPlayer = seatId < 2
        gameReady = len(self.table.penguins) > 1
        if isPlayer and gameReady:
            movie, direction, spade = data.Move
            currentPlayer = self.table.penguins[self.table.game.currentPlayer - 1]
            if currentPlayer != self:
                return
            if not self.table.game.isValidMove(movie, direction, int(spade)):
                return
            self.table.game.makeMove(movie, direction, int(spade))
            self.table.sendXt("zm", movie, direction, spade)
            opponent = self.table.penguins[1 if self.table.game.currentPlayer == 1 else 0]
            if self.table.game.turns == 0:
                winnings = self.table.game.determineWinnings()
                self.sendCoins(self.user.Coins + winnings)
                opponent.sendCoins(opponent.user.Coins + winnings)
                self.table.reset()
                return
            self.table.game.currentPlayer = 2 if self.table.game.currentPlayer == 1 else 1
    except ValueError:
        self.logger.warn("Malformed move.".format(self.user.Username))

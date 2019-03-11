from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.Table import TableHandler

class FindFour(object):

    def __init__(self):
        self.currentPlayer = 1
        self.board = [[0 for row in range(6)] for column in range(7)]

    def placeChip(self, column, row):
        self.board[column][row] = self.currentPlayer

    def isPositionWin(self, column, row):
        for deltaRow, deltaColumn in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            streak = 1
            for delta in (1, -1):
                deltaRow *= delta
                deltaColumn *= delta
                nextRow = row + deltaRow
                nextColumn = column + deltaColumn
                while 0 <= nextRow < 6 and 0 <= nextColumn < 7:
                    if self.board[nextColumn][nextRow] == self.currentPlayer:
                        streak += 1
                    else:
                        break
                    if streak == 4:
                        return True
                    nextRow += deltaRow
                    nextColumn += deltaColumn
        return False

    def isValidMove(self, column, row):
        if 0 <= row <= 5 and 0 <= column <= 6:
            if row == 5 or (self.board[column][row] == 0 and self.board[column][row + 1]):
                return True
        return False

    def isBoardFull(self):
        for column in self.board:
            if not column[0]:
                return False
        return True

    def getString(self):
        return ",".join(str(item) for row in self.board for item in row)

@Handlers.Handle(XT.GetGame)
@TableHandler(FindFour)
def handleGetGame(self, data):
    self.sendXt("gz", self.table.getString())

@Handlers.Handle(XT.JoinGame)
@TableHandler(FindFour)
def handleJoinGame(self, data):
    gameFull = len(self.table.penguins) > 2
    if not gameFull:
        seatId = self.table.getSeatId(self)
        self.sendXt("jz", seatId)
        self.table.sendXt("uz", seatId, self.user.SafeName)

        if len(self.table.penguins) == 2:
            self.table.sendXt("sz")

@Handlers.Handle(XT.SendMove)
@TableHandler(FindFour)
def handleSendMove(self, data):
    try:
        seatId = self.table.getSeatId(self)
        isPlayer = seatId < 2
        gameReady = len(self.table.penguins) > 1
        if isPlayer and gameReady:
            column, row = map(int, data.Move)
            currentPlayer = self.table.penguins[self.table.game.currentPlayer - 1]
            if currentPlayer != self:
                return
            if not self.table.game.isValidMove(column, row):
                return
            self.table.sendXt("zm", self.table.game.currentPlayer - 1, column, row)
            self.table.game.placeChip(column, row)
            opponent = self.table.penguins[1 if self.table.game.currentPlayer == 1 else 0]
            if self.table.game.isPositionWin(column, row):
                self.sendCoins(self.user.Coins + 10)
                opponent.sendCoins(opponent.user.Coins + 5)
                self.table.reset()
                return
            if self.table.game.isBoardFull():
                self.sendCoins(self.user.Coins + 5)
                opponent.sendCoins(opponent.user.Coins + 5)
                self.table.reset()
                return
            self.table.game.currentPlayer = 2 if self.table.game.currentPlayer == 1 else 1
    except ValueError:
        self.logger.warn("Malformed move.".format(self.user.Username))

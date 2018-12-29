from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.Table import TableHandler

class Mancala(object):

    def __init__(self):
        self.currentPlayer = 1
        self.board = [
            4, 4, 4, 4, 4, 4, 0,
            4, 4, 4, 4, 4, 4, 0
        ]

    def makeMove(self, hollow):
        capture = False
        hand = self.board[hollow]
        self.board[hollow] = 0

        while hand > 0:
            hollow = hollow + 1 if hollow + 1 < len(self.board) else 0
            myMancala, opponentMancala = (6, 13) if self.currentPlayer == 1 else (13, 6)
            if hollow == opponentMancala:
                continue
            oppositeHollow = 12 - hollow
            if self.currentPlayer == 1 and hollow in range(0, 6) and hand == 1 and self.board[hollow] == 0:
                self.board[myMancala] = self.board[myMancala] + self.board[oppositeHollow] + 1
                self.board[oppositeHollow] = 0
                capture = True
                break
            if self.currentPlayer == 2 and hollow in range(7, 13) and hand == 1 and self.board[hollow] == 0:
                self.board[myMancala] = self.board[myMancala] + self.board[oppositeHollow] + 1
                self.board[oppositeHollow] = 0
                capture = True
                break
            self.board[hollow] += 1
            hand -= 1
        if (self.currentPlayer == 1 and hollow != 6) or (self.currentPlayer == 2 and hollow != 13):
            return "c" if capture else str()
        else:
            self.currentPlayer = 2 if self.currentPlayer == 1 else 1
            return "f"

    def isValidMove(self, hollow):
        if self.currentPlayer == 1 and hollow not in range(0, 6):
            return False
        elif self.currentPlayer == 2 and hollow not in range(7, 13):
            return False
        return True

    def determineTie(self):
        if sum(self.board[0:6]) == 0 or sum(self.board[7:-1]) == 0:
            if sum(self.board[0:6]) == sum(self.board[7:-1]):
                return True
        return False

    def determineWin(self):
        if sum(self.board[0:6]) == 0 or sum(self.board[7:-1]) == 0:
            if sum(self.board[0:6]) > sum(self.board[7:-1]):
                return self.currentPlayer == 1
            return self.currentPlayer == 2
        return False

    def getString(self):
        return ','.join(map(str, self.board))

@Handlers.Handle(XT.GetGame)
@TableHandler(Mancala)
def handleGetGame(self, data):
    self.sendXt("gz", self.table.getString())

@Handlers.Handle(XT.JoinGame)
@TableHandler(Mancala)
def handleJoinGame(self, data):
    gameFull = len(self.table.penguins) > 2
    if not gameFull:
        seatId = self.table.getSeatId(self)
        self.sendXt("jz", seatId)
        self.table.sendXt("uz", seatId, self.user.Nickname)

        if len(self.table.penguins) == 2:
            self.table.sendXt("sz", 0)

@Handlers.Handle(XT.SendMove)
@TableHandler(Mancala)
def handleSendMove(self, data):
    seatId = self.table.getSeatId(self)
    isPlayer = seatId < 2
    gameReady = len(self.table.penguins) > 1
    if isPlayer and gameReady:
        hollow, = map(int, data.Move)
        currentPlayer = self.table.penguins[self.table.game.currentPlayer - 1]
        if currentPlayer != self:
            return
        if not self.table.game.isValidMove(hollow):
            return
        moveResult = self.table.game.makeMove(hollow)
        self.table.sendXt("zm", seatId, hollow, moveResult)
        opponent = self.table.penguins[1 if self.table.game.currentPlayer == 1 else 0]
        if self.table.game.determineWin():
            self.sendCoins(self.user.Coins + 10)
            opponent.sendCoins(opponent.user.Coins + 5)
            self.table.reset()
            return
        elif self.table.game.determineTie():
            self.sendCoins(self.user.Coins + 5)
            opponent.sendCoins(opponent.user.Coins + 5)
            self.table.reset()
            return
        self.table.game.currentPlayer = 2 if self.table.game.currentPlayer == 1 else 1

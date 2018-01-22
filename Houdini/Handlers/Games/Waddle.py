from Houdini.Handlers import Handlers, XT

class SledRace(object):

    def __init__(self, penguins, seats):
        self.penguins = penguins
        self.seats = seats

        for penguin in self.penguins:
            penguin.room.remove(penguin)
            penguin.server.rooms[999].add(penguin)

            penguin.waddle = self

    def remove(self, penguin):
        self.penguins.remove(penguin)
        penguin.waddle = None

        penguins = []
        for penguin in self.penguins:
            penguins.append("|".join([penguin.user.Username, str(penguin.user.Color),
                                      str(penguin.user.Hand), penguin.user.Username]))
        self.sendXt("uz", self.seats, "%".join(penguins))

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

class Waddle(object):

    def __init__(self, id, seats, game, room):
        self.id = id
        self.seats = seats
        self.game = game
        self.room = room

        self.penguins = [None] * seats

    def add(self, penguin):
        seatId = self.penguins.index(None)
        self.penguins[seatId] = penguin
        penguin.sendXt("jw", seatId)
        self.room.sendXt("uw", self.id, seatId, penguin.user.Username)

        penguin.waddle = self

        if self.penguins.count(None) == 0:
            self.game(list(self.penguins), self.seats)
            self.reset()

    def remove(self, penguin):
        seatId = self.getSeatId(penguin)
        self.penguins[seatId] = None
        self.room.sendXt("uw", self.id, seatId)

        penguin.waddle = None

    def reset(self):
        for seatId, penguin in enumerate(self.penguins):
            if penguin:
                self.penguins[seatId] = None
                self.room.sendXt("uw", self.id, seatId)

    def getSeatId(self, penguin):
        return self.penguins.index(penguin)

def WaddleHandler(waddle):
    def handlerFunction(function):
        def handler(penguin, data):
            if penguin.waddle and type(penguin.waddle) == waddle:
                function(penguin, data)
            return function
        return handler
    return handlerFunction

def leaveWaddle(self):
    if self.waddle:
        self.waddle.remove(self)

@Handlers.Handle(XT.GetWaddlePopulation)
def handleGetWaddlePopulation(self, data):
    try:
        waddles = []
        for waddleId in data.Waddles:
            waddle = self.room.waddles[int(waddleId)]
            penguinNames = ",".join((penguin.user.Username if penguin else str() for penguin in waddle.penguins))
            waddles.append(waddleId + "|" + penguinNames)
        self.sendXt("gw", "%".join(waddles))
    except KeyError:
        self.logger.warn("Waddle does not exist!")

@Handlers.Handle(XT.JoinWaddle)
def handleJoinWaddle(self, data):
    try:
        if not self.waddle:
            waddle = self.room.waddles[data.WaddleId]
            waddle.add(self)
    except KeyError:
        self.logger.warn("{} Tried to join a waddle which does not exist!"
                         .format(self.user.Username))

@Handlers.Handle(XT.LeaveWaddle)
def handleLeaveWaddle(self, data):
    if self.waddle:
        self.waddle.remove(self)

@Handlers.Handle(XT.JoinGame)
@WaddleHandler(SledRace)
def handleJoinGame(self, data):
    penguins = []
    for penguin in self.waddle.penguins:
        penguins.append("|".join([penguin.user.Username, str(penguin.user.Color),
                                  str(penguin.user.Hand), penguin.user.Username]))
    self.sendXt("uz", self.waddle.seats, "%".join(penguins))

@Handlers.Handle(XT.SendMove)
@WaddleHandler(SledRace)
def handleSendMove(self, data):
    playerId, x, y, gameTime = map(int, data.Move)
    realPlayerId = self.waddle.penguins.index(self)
    if playerId != realPlayerId:
        return
    self.waddle.sendXt("zm", playerId, x, y, gameTime)

@Handlers.Handle(XT.GameOver)
@WaddleHandler(SledRace)
def handleGameOver(self, data):
    position = data.Score
    coins = (20, 10, 5, 5)[position - 1]
    self.sendCoins(self.user.Coins + coins)
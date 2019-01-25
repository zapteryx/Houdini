from Houdini.Handlers import Handlers, XT

class Waddle(object):

    def __init__(self, id, seats, game, room):
        self.id = id
        self.seats = seats
        self.game = game
        self.room = room

        self.penguins = [None] * seats

    def add(self, penguin):
        if penguin.user.Moderator != 2:
            seatId = self.penguins.index(None)
            self.penguins[seatId] = penguin
            penguin.sendXt("jw", seatId)
            self.room.sendXt("uw", self.id, seatId, penguin.user.Nickname)

            penguin.waddle = self

            if self.penguins.count(None) == 0:
                self.game(list(self.penguins), self.seats)
                self.reset()

    def remove(self, penguin):
        if penguin.user.Moderator != 2:
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

def WaddleHandler(*waddle):
    def handlerFunction(function):
        def handler(penguin, data):
            if penguin.waddle and type(penguin.waddle) in waddle:
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
            penguinNames = ",".join((penguin.user.Nickname if penguin else str() for penguin in waddle.penguins))
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

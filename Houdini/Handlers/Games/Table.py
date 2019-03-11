from Houdini.Handlers import Handlers, XT

class Table(object):

    def __init__(self, id, game, room):
        self.id = id
        self.game = game()
        self.room = room

        self.penguins = []

    def add(self, penguin):
        if penguin.user.Moderator != 2:
            self.penguins.append(penguin)

            seatId = len(self.penguins) - 1

            penguin.sendXt("jt", self.id, seatId + 1)
            self.room.sendXt("ut", self.id, len(self.penguins))
            penguin.table = self

            return seatId

    def remove(self, penguin):
        if penguin.user.Moderator != 2:
            self.penguins.remove(penguin)

            penguin.sendXt("lt")
            self.room.sendXt("ut", self.id, len(self.penguins))
            penguin.table = None

    def reset(self):
        for penguin in self.penguins:
            penguin.table = None

        self.game = type(self.game)()
        self.penguins = []
        self.room.sendXt("ut", self.id, 0)

    def getSeatId(self, penguin):
        return self.penguins.index(penguin)

    def getString(self):
        if len(self.penguins) == 0:
            return str()
        elif len(self.penguins) == 1:
            playerOne, = self.penguins
            return "%".join([playerOne.user.SafeName, str(), self.game.getString()])
        playerOne, playerTwo = self.penguins[:2]
        if len(self.penguins) == 2:
            return "%".join([playerOne.user.SafeName, playerTwo.user.SafeName, self.game.getString()])
        return "%".join([playerOne.user.SafeName, playerTwo.user.SafeName, self.game.getString(), "1"])

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

def TableHandler(game):
    def handlerFunction(function):
        def handler(penguin, data):
            if penguin.table and type(penguin.table.game) == game:
                function(penguin, data)
            return function
        return handler
    return handlerFunction

def leaveTable(self):
    if self.table:
        seatId = self.table.getSeatId(self)
        isPlayer = seatId < 2
        gameReady = len(self.table.penguins) > 1
        if isPlayer and gameReady:
            self.table.sendXt("cz", self.user.SafeName)
            self.table.reset()
        else:
            self.table.remove(self)

@Handlers.Handle(XT.GetTablePopulation)
def handleGetTablePopulation(self, data):
    try:
        tablesString = []
        for tableId in data.Tables:
            table = self.room.tables[int(tableId)]
            tablesString.append("{}|{}".format(tableId, len(table.penguins)))
        self.sendXt("gt", "%".join(tablesString))
    except KeyError:
        self.logger.warn("{} table does not exist.".format(self.user.Username))

@Handlers.Handle(XT.JoinTable)
def handleJoinTable(self, data):
    try:
        if not self.table:
            table = self.room.tables[data.TableId]
            table.add(self)
    except KeyError:
        self.logger.warn("{} tried to join a table which doesn't exist."
                         .format(self.user.Username))

@Handlers.Handle(XT.LeaveTable)
def handleLeaveTable(self, data):
    leaveTable(self)

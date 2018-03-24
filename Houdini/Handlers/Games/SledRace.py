from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.Waddle import WaddleHandler

class SledRace(object):

    def __init__(self, penguins, seats):
        self.penguins = penguins
        self.seats = seats

        for penguin in self.penguins:
            penguin.joinRoom(999)

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
    try:
        playerId, x, y, gameTime = map(float, data.Move)
        realPlayerId = self.waddle.penguins.index(self)
        if playerId != realPlayerId:
            return
        self.waddle.sendXt("zm", playerId, x, y, gameTime)
    except ValueError:
        self.logger.debug("Invalid sled race move!")

@Handlers.Handle(XT.GameOver)
@WaddleHandler(SledRace)
def handleGameOver(self, data):
    position = data.Score
    coins = (20, 10, 5, 5)[position - 1]
    self.sendCoins(self.user.Coins + coins)
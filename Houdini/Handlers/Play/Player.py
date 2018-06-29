from Houdini import Cache
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from sqlalchemy.sql import select


@Cache("houdini.player")
def getPlayerString(self, penguinId, playerTuple = None):
    if penguinId in self.server.players:
        player = self.server.players[penguinId]
        playerTuple = (player.user.ID, player.user.Nickname, player.user.Approval, player.user.Color, player.user.Head,
                       player.user.Face, player.user.Neck, player.user.Body, player.user.Hand,
                       player.user.Feet, player.user.Flag, player.user.Photo)
    if playerTuple is not None:
        playerData = [str(playerDetail) for playerDetail in playerTuple]
        return "|".join(playerData)
    return createPlayerString(self, penguinId)

@inlineCallbacks
def createPlayerString(self, penguinId):
    playerTuple = yield self.engine.first(select(
        [Penguin.c.ID, Penguin.c.Nickname, Penguin.c.Approval, Penguin.c.Color, Penguin.c.Head,
         Penguin.c.Face, Penguin.c.Neck, Penguin.c.Body, Penguin.c.Hand, Penguin.c.Feet, Penguin.c.Flag,
         Penguin.c.Photo]).where(Penguin.c.ID == penguinId))
    getPlayerString.invalidate(self, penguinId)
    if playerTuple is not None:
        cachedPlayerString = getPlayerString(self, penguinId, playerTuple)
        returnValue(cachedPlayerString)
    returnValue(str())

@Handlers.Handle(XT.Heartbeat)
@Handlers.Throttle(60)
def handleSendHeartbeat(self, data):
    self.sendXt("h")
    

@Handlers.Handle(XT.ThrowBall)
@Handlers.Throttle()
def handlePlayerThrowBall(self, data):
    self.room.sendXt("sb", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerMove)
def handleSendPlayerMove(self, data):
    self.x = data.X
    self.y = data.Y

    self.room.sendXt("sp", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerAction)
@Handlers.Throttle()
def handleUpdatePlayerAction(self, data):
    self.room.sendXt("sa", self.user.ID, data.Id)

@Handlers.Handle(XT.SendEmote)
@Handlers.Throttle()
def handleSendEmote(self, data):
    self.room.sendXt("se", self.user.ID, data.Id)

@Handlers.Handle(XT.PlayerFrame)
@Handlers.Throttle()
def handleSendPlayerFrame(self, data):
    self.frame = data.Id
    self.room.sendXt("sf", self.user.ID, data.Id)

@Handlers.Handle(XT.SendJoke)
@Handlers.Throttle()
def handleSendJoke(self, data):
    self.room.sendXt("sj", self.user.ID, data.Id)

@Handlers.Handle(XT.SendSafe)
@Handlers.Throttle()
def handleSafeMessage(self, data):
    self.room.sendXt("ss", self.user.ID, data.Id)

@Handlers.Handle(XT.SendTourGuide)
@Handlers.Throttle()
def handleSendTourGuide(self, data):
    self.room.sendXt("sg", self.user.ID, data.Id)

@Handlers.Handle(XT.SendLineMessage)
@Handlers.Throttle()
def handleSendLineMessage(self, data):
    self.room.sendXt("sl", self.user.ID, data.Id)

@Handlers.Handle(XT.SendMascotMessage)
@Handlers.Throttle()
def handleSendMascotMessage(self, data):
    if self.user.MascotStamp:
        self.room.sendXt("sma", self.user.ID, data.Id)

@Handlers.Handle(XT.GetLatestRevision)
@Handlers.Throttle(-1)
def handleGetLatestRevision(self, data):
    self.room.sendXt("glr", "0")


@Handlers.Handle(XT.GetPlayer)
@Handlers.Throttle()
@inlineCallbacks
def handleLoadPlayerObject(self, data):
    playerString = yield getPlayerString(self, data.Id)
    self.sendXt("gp", playerString)
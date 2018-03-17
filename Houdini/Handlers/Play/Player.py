from beaker.cache import cache_region as Cache

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Cache("houdini", "player")
def getPlayerString(self, penguinId):
    playerTuple = self.session.query(Penguin.ID, Penguin.Nickname, Penguin.Approval, Penguin.Color, Penguin.Head,
                                     Penguin.Face, Penguin.Neck, Penguin.Body, Penguin.Hand, Penguin.Feet, Penguin.Flag,
                                     Penguin.Photo).filter_by(ID=penguinId).first()
    if playerTuple is not None:
        playerData = [str(playerDetail) for playerDetail in playerTuple]
        return "|".join(playerData)
    return str()

@Handlers.Handle(XT.Heartbeat)
@Handlers.Throttle(60)
def handleSendHeartbeat(self, data):
    self.sendXt("h")

@Handlers.Handle(XT.ThrowBall)
@Handlers.Throttle(1)
def handlePlayerThrowBall(self, data):
    self.room.sendXt("sb", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerMove)
def handleSendPlayerMove(self, data):
    self.x = data.X
    self.y = data.Y

    self.room.sendXt("sp", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerAction)
@Handlers.Throttle(1)
def handleUpdatePlayerAction(self, data):
    self.room.sendXt("sa", self.user.ID, data.Id)

@Handlers.Handle(XT.SendEmote)
@Handlers.Throttle(1)
def handleSendEmote(self, data):
    self.room.sendXt("se", self.user.ID, data.Id)

@Handlers.Handle(XT.PlayerFrame)
@Handlers.Throttle(1)
def handleSendPlayerFrame(self, data):
    self.frame = data.Id
    self.room.sendXt("sf", self.user.ID, data.Id)

@Handlers.Handle(XT.SendJoke)
@Handlers.Throttle(1)
def handleSendJoke(self, data):
    self.room.sendXt("sj", self.user.ID, data.Id)

@Handlers.Handle(XT.SendSafe)
@Handlers.Throttle(1)
def handleSafeMessage(self, data):
    self.room.sendXt("ss", self.user.ID, data.Id)

@Handlers.Handle(XT.SendTourGuide)
@Handlers.Throttle(1)
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
def handleLoadPlayerObject(self, data):
    playerTuple = self.session.query(Penguin.ID, Penguin.Username, Penguin.Color, Penguin.Head, Penguin.Face,
                                     Penguin.Neck, Penguin.Body, Penguin.Hand, Penguin.Feet, Penguin.Flag,
                                     Penguin.Photo).filter_by(ID=data.Id).first()

    if playerTuple is not None:
        playerData = [str(playerDetail) for playerDetail in playerTuple]
        playerData.insert(2, "1")

        playerString = "|".join(playerData)

        self.sendXt("gp", playerString)
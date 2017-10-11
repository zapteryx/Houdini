from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.Heartbeat)
def handleSendHeartbeat(self, data):
    self.sendXt("h")

@Handlers.Handle(XT.ThrowBall)
def handlePlayerThrowBall(self, data):
    self.room.sendXt("sb", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerMove)
def handleSendPlayerMove(self, data):
    self.x = data.X
    self.y = data.Y

    self.room.sendXt("sp", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerAction)
def handleUpdatePlayerAction(self, data):
    self.room.sendXt("sa", self.user.ID, data.Id)

@Handlers.Handle(XT.SendEmote)
def handleSendEmote(self, data):
    self.room.sendXt("se", self.user.ID, data.Id)

@Handlers.Handle(XT.PlayerFrame)
def handleSendPlayerFrame(self, data):
    self.frame = data.Id
    self.room.sendXt("sf", self.user.ID, data.Id)

@Handlers.Handle(XT.SendJoke)
def handleSendJoke(self, data):
    self.room.sendXt("sj", self.user.ID, data.Id)

@Handlers.Handle(XT.SendSafe)
def handleSafeMessage(self, data):
    self.room.sendXt("ss", self.user.ID, data.Id)

@Handlers.Handle(XT.SendTourGuide)
def handleSendTourGuide(self, data):
    self.room.sendXt("sg", self.user.ID, data.Id)

@Handlers.Handle(XT.GetLatestRevision)
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
from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.Message)
@Handlers.Throttle(0.5)
def handleSendMessage(self, data):
    if data.Id != self.user.ID:
        return self.transport.loseConnection()

    self.room.sendXt("sm", self.user.ID, data.Message)
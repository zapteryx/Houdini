from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.Message)
@Handlers.Throttle(0.5)
def handleSendMessage(self, data):
    if data.Id != self.user.ID:
        return self.transport.loseConnection()

    if not self.user.Active:
        return self.transport.loseConnection()

    if self.muted:
        for roomPlayer in self.room.players:
            if roomPlayer.user.Moderator:
                roomPlayer.sendXt("mm", data.Message, self.user.ID)
        return

    self.room.sendXt("sm", self.user.ID, data.Message)

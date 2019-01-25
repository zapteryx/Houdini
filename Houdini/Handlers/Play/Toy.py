from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.OpenBook)
@Handlers.Throttle()
def handleOpenPlayerBook(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("at", self.user.ID, data.ToyId)

@Handlers.Handle(XT.CloseBook)
@Handlers.Throttle()
def handleClosePlayerBook(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("rt", self.user.ID)

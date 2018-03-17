from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.OpenBook)
@Handlers.Throttle()
def handleOpenPlayerBook(self, data):
    self.room.sendXt("at", self.user.ID)

@Handlers.Handle(XT.CloseBook)
@Handlers.Throttle()
def handleClosePlayerBook(self, data):
    self.room.sendXt("rt", self.user.ID)
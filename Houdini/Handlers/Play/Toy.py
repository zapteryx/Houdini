from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.OpenBook)
def handleOpenPlayerBook(self, data):
    self.room.sendXt("at", self.user.ID)

@Handlers.Handle(XT.CloseBook)
def handleClosePlayerBook(self, data):
    self.room.sendXt("rt", self.user.ID)
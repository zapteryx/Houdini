from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.GetPuffles)
def handleGetPuffles(self, data):
    self.sendXt("pg", "")
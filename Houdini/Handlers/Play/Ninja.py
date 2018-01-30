from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.GetNinjaRanks)
def handleGetNinjaRanks(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gnr", data.PlayerId, self.user.NinjaRank, 0, 0, 0)

@Handlers.Handle(XT.GetNinjaLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gnl", self.user.NinjaRank, self.user.NinjaProgress)

@Handlers.Handle(XT.GetCards)
def handleGetCards(self, data):
    self.sendXt("gcd", self.user.Deck)
from Houdini.Handlers import Handlers, XT


@Handlers.Handle(XT.GetNinjaRanks)
def handleGetNinjaRanks(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gnr", data.PlayerId, self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank, self.user.SnowNinjaRank)


@Handlers.Handle(XT.GetNinjaLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gnl", self.user.NinjaRank, self.user.NinjaProgress, 10)


@Handlers.Handle(XT.GetNinjaFireLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gfl", self.user.FireNinjaRank, self.user.FireNinjaProgress, 5)


@Handlers.Handle(XT.GetNinjaWaterLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gwl", self.user.WaterNinjaRank, self.user.WaterNinjaProgress, 5)


@Handlers.Handle(XT.GetNinjaSnowLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gsl", self.user.SnowNinjaRank, self.user.SnowNinjaProgress, 24)


@Handlers.Handle(XT.GetCards)
def handleGetCards(self, data):
    deckString = "|".join(["{},{},0".format(cardId, cardQuantity) for cardId, cardQuantity in self.deck.iteritems()])
    self.sendXt("gcd", deckString)

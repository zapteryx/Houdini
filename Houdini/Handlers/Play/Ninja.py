from Houdini.Handlers import Handlers, XT


@Handlers.Handle(XT.GetNinjaRanks)
def handleGetNinjaRanks(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gnr", data.PlayerId, self.user.NinjaRank, self.user.FireNinjaRank, self.user.WaterNinjaRank)


@Handlers.Handle(XT.GetNinjaLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gnl", self.user.NinjaRank, self.user.NinjaProgress)


@Handlers.Handle(XT.GetNinjaFireLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gfl", self.user.FireNinjaRank, self.user.FireNinjaProgress)


@Handlers.Handle(XT.GetNinjaWaterLevel)
def handleGetNinjaLevel(self, data):
    self.sendXt("gwl", self.user.WaterNinjaRank, self.user.WaterNinjaProgress)


@Handlers.Handle(XT.GetCards)
def handleGetCards(self, data):
    deckString = "|".join(["{},{}".format(cardId, cardQuantity) for cardId, cardQuantity in self.deck.iteritems()])
    self.sendXt("gcd", deckString)
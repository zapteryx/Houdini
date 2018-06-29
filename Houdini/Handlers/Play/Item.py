from Houdini import Cache
from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Play.Moderation import cheatBan
from Houdini.Data.Penguin import Inventory

cardStarterDeckId = 821
fireBoosterDeckId = 8006
waterBoosterDeckId = 8010

boosterDecks = {
    cardStarterDeckId: [1, 6, 9, 14, 17, 20, 22, 23, 26, 73, 89, 81],
    fireBoosterDeckId: [3, 18, 216, 222, 229, 303, 304, 314, 319, 250, 352],
    waterBoosterDeckId: [202, 204, 305, 15, 13, 312, 218, 220, 29, 90]
}

rankAwards = [4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 104]
beltPostcards = {1: 177, 5: 178, 9: 179}
beltStamps = {1: 230, 5: 232, 9: 234, 10: 236}

@Handlers.Handle(XT.BuyInventory)
@Handlers.Throttle()
def handleBuyInventory(self, data):
    if data.ItemId not in self.server.items:
        return self.sendError(402)

    elif data.ItemId in self.inventory:
        return self.sendError(400)

    if self.server.items.isBait(data.ItemId):
        return cheatBan(self, self.user.ID, comment="Added bait item")

    if self.server.items.isTourGuide(data.ItemId):
        self.receiveSystemPostcard(126)

    if data.ItemId in boosterDecks:
        self.addCards(*boosterDecks[data.ItemId])

    itemCost = self.server.items.getCost(data.ItemId)

    if self.user.Coins < itemCost:
        return self.sendError(401)

    self.addItem(data.ItemId, itemCost)

    getPinString.invalidate(self, self.user.ID)
    getAwardsString.invalidate(self, self.user.ID)

@Handlers.Handle(XT.GetInventory)
@Handlers.Throttle(-1)
def handleGetInventory(self, data):
    self.sendXt("gi", "%".join(map(str, self.inventory)))

@Cache("houdini.pins")
def getPinString(self, penguinId, inventory = None):
    def getString(pinId):
        isMember = int(self.server.items[pinId].Member)
        timestamp = self.server.pins.getUnixTimestamp(pinId)
        return "|".join(map(str, [pinId, timestamp, isMember]))

    if penguinId in self.server.players:
        inventory = self.server.players[penguinId].inventory

    if inventory is not None:
        pins = [getString(itemId) for itemId in inventory if self.server.items.isItemPin(itemId)]
        return "%".join(pins)

    return createItemString(self, penguinId, getPinString)

@Cache("houdini.awards")
def getAwardsString(self, penguinId, inventory = None):
    if penguinId in self.server.players:
        inventory = self.server.players[penguinId].inventory

    if inventory is not None:
        pins = [str(itemId) for itemId in inventory if self.server.items.isItemAward(itemId)]
        return "%".join(pins)

    return createItemString(self, penguinId, getAwardsString)

@inlineCallbacks
def createItemString(self, penguinId, cacheBuilder):

    cacheBuilder.invalidate(self, penguinId)
    cachedItemString = cacheBuilder(self, penguinId, inventory)
    returnValue(cachedItemString)


@Handlers.Handle(XT.GetPlayerPins)
@Handlers.Throttle()
@inlineCallbacks
def handleGetPlayerPins(self, data):
    pinString = yield getPinString(self, data.PlayerId)
    self.sendXt("qpp", pinString)


@Handlers.Handle(XT.GetPlayerAwards)
@Handlers.Throttle()
@inlineCallbacks
def handleGetPlayerAwards(self, data):
    awardsString = yield getAwardsString(self, data.PlayerId)
    self.sendXt("qpa", data.PlayerId, awardsString)
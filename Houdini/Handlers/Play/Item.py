from beaker.cache import cache_region as Cache, region_invalidate as Invalidate

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

@Handlers.Handle(XT.BuyInventory)
def handleBuyInventory(self, data):
    if data.ItemId not in self.server.items:
        return self.sendError(402)

    if data.ItemId in self.inventory:
        return self.sendError(400)

    if self.server.serverName == "Redemption":
        return self.transport.loseConnection()
    else:
        if data.ItemId in self.server.availableClothing["EliteGear"]:
            return self.sendError(402)
        elif data.ItemId not in self.server.availableClothing["Standard"] and \
                data.ItemId not in self.server.availableClothing["Mascot"]:
            return self.sendError(402)

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

    Invalidate(getPinString, 'houdini', 'pins', self.user.ID)
    Invalidate(getAwardsString, 'houdini', 'awards', self.user.ID)

@Handlers.Handle(XT.GetInventory)
@Handlers.Throttle(-1)
def handleGetInventory(self, data):
    self.sendXt("gi", "%".join(map(str, self.inventory)))


@Cache('houdini', 'pins')
def getPinString(self, penguinId):
    def getString(pinId):
        isMember = int(self.server.items[pinId].Member)
        timestamp = self.server.pins.getUnixTimestamp(pinId)
        return "|".join(map(str, [pinId, timestamp, isMember]))

    if penguinId in self.server.players:
        pinsArray = [getString(itemId) for itemId in self.server.players[penguinId].inventory
                     if itemId in self.server.pins]
    else:
        pinsArray = [getString(itemId) for itemId, in self.session.query(Inventory.ItemID)
            .filter_by(PenguinID=penguinId) if itemId in self.server.pins]

    pinsArray.sort(key=lambda x: x.split("|")[1])
    return "%".join(pinsArray)


@Cache('houdini', 'awards')
def getAwardsString(self, penguinId):
    if penguinId in self.server.players:
        awardsArray = [str(itemId) for itemId in self.server.players[penguinId].inventory
                       if self.server.items.isItemAward(itemId)]
    else:
        awardsArray = [str(itemId) for itemId, in self.session.query(Inventory.ItemID)
            .filter_by(PenguinID=penguinId) if self.server.items.isItemAward(itemId)]

    return "|".join(awardsArray)


@Handlers.Handle(XT.GetPlayerPins)
@Handlers.Throttle()
def handleGetPlayerPins(self, data):
    self.sendXt("qpp", getPinString(self, data.PlayerId))


@Handlers.Handle(XT.GetPlayerAwards)
@Handlers.Throttle()
def handleGetPlayerAwards(self, data):
    self.sendXt("qpa", data.PlayerId, getAwardsString(self, data.PlayerId))

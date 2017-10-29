from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Play.Moderation import cheatBan
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.BuyInventory)
def handleBuyInventory(self, data):
    if data.ItemId not in self.server.items:
        return self.sendError(402)

    elif data.ItemId in self.inventory:
        return self.sendError(400)

    if self.server.items.isBait(data.ItemId):
        return cheatBan(self, self.user.ID, comment="Added bait item")

    itemCost = self.server.items.getCost(data.ItemId)

    if self.user.Coins < itemCost:
        return self.sendError(401)

    self.addItem(data.ItemId, itemCost)

@Handlers.Handle(XT.GetInventory)
def handleGetInventory(self, data):
    inventoryArray = self.user.Inventory.split("%")

    try:
        inventoryArray = [int(itemId) for itemId in inventoryArray]
        self.inventory = inventoryArray

    except ValueError:
        self.inventory = []

    finally:
        self.sendXt("gi", self.user.Inventory)

@Handlers.Handle(XT.GetPlayerPins)
def handleGetPlayerPins(self, data):
    player = self.session.query(Penguin.Inventory).\
        filter(Penguin.ID == data.PlayerId).first()

    if player is None:
        return self.transport.loseConnection()

    inventory = player.Inventory.split("%")
    pinsArray = []

    for itemId in inventory:
        if self.server.items.isItemPin(itemId):
            isMember = int(self.server.items[int(itemId)].Member)
            timestamp = self.server.pins[int(itemId)]["unix"]
            pinString = "|".join([itemId, str(timestamp), str(isMember)])
            pinsArray.append(pinString)

    self.sendXt("qpp", "%".join(pinsArray))

@Handlers.Handle(XT.GetPlayerAwards)
def handleGetPlayerAwards(self, data):
    player = self.session.query(Penguin.Inventory).\
        filter(Penguin.ID == data.PlayerId).first()

    if player is None:
        return self.transport.loseConnection()

    inventory = player.Inventory.split("%")
    awardsArray = []

    for itemId in inventory:
        if self.server.items.isItemAward(itemId):
            awardsArray.append(itemId)

    self.sendXt("qpa", data.PlayerId, "%".join(awardsArray))
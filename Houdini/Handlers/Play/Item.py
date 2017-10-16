from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.BuyInventory)
def handleBuyInventory(self, data):
    if data.ItemId not in self.server.items:
        return self.sendError(402)

    elif data.ItemId in self.inventory:
        return self.sendError(400)

    itemCost = int(self.server.items[data.ItemId]["cost"])

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
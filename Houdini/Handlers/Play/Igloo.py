from Houdini import Cache
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Igloo import Igloo, IglooFurniture


@Cache("houdini.igloo")
def getIglooString(self, penguinId, iglooString = None):
    if iglooString is not None:
        return iglooString
    return createIglooString(self, penguinId)

@inlineCallbacks
def createIglooString(self, penguinId):
    if igloo is None:

    furnitureString = ",".join(["{}|{}|{}|{}|{}".format(furniture.FurnitureID, furniture.X, furniture.Y,
                                                        furniture.Rotation, furniture.Frame)
                                for furniture in iglooFurniture])
    iglooString = "%".join(map(str, [penguinId, igloo.Type, igloo.Music, igloo.Floor, furnitureString]))

    getIglooString.invalidate(self, penguinId)
    cachedIglooString = getIglooString(self, penguinId, iglooString)
    returnValue(cachedIglooString)


@Handlers.Handle(XT.SendActivateIgloo)
def handleSendActivateIgloo(self, data):
    iglooType = data.TypeId

    if iglooType in self.igloos:
        self.igloo.Type = iglooType
        self.igloo.Floor = 0


@Handlers.Handle(XT.GetIglooDetails)
@Handlers.Throttle()
@inlineCallbacks
def handleGetIglooDetails(self, data):
    if data.Id != self.user.ID and data.Id not in self.buddies \
            and data.Id not in self.server.openIgloos:
        returnValue(self.transport.loseConnection())

    iglooString = yield getIglooString(self, data.Id)
    self.sendXt("gm", iglooString)


@Handlers.Handle(XT.GetOwnedIgloos)
def handleGetOwnedIgloos(self, data):
    self.sendXt("go", "|".join(map(str, self.igloos)))


@Handlers.Handle(XT.UpdateIglooMusic)
def handleUpdateIglooMusic(self, data):
    self.igloo.Music = data.MusicId


@Handlers.Handle(XT.GetFurnitureList)
def handleGetFurnitureList(self, data):
    furnitureString = "%".join(["{}|{}".format(furnitureId, quantity)
                                for furnitureId, quantity in self.furniture.items()])
    self.sendXt("gf", furnitureString)


@Handlers.Handle(XT.UpdateFloor)
def handleUpdateFloor(self, data):
    if data.FloorId not in self.server.floors:
        return self.sendError(402)

    floorCost = self.server.floors.getCost(data.FloorId)

    if floorCost > self.user.Coins:
        return self.sendError(401)

    self.addFlooring(data.FloorId, floorCost)


@Handlers.Handle(XT.UpdateIglooType)
def handleUpdateIglooType(self, data):
    if data.IglooId not in self.server.igloos:
        return self.sendError(402)

    iglooCost = self.server.igloos.getCost(data.IglooId)

    if iglooCost > self.user.Coins:
        return self.sendError(401)

    if data.IglooId in self.igloos:
        return self.sendError(500)

    self.addIgloo(data.IglooId, iglooCost)


@Handlers.Handle(XT.BuyFurniture)
def handleBuyFurniture(self, data):
    if data.FurnitureId not in self.server.furniture:
        return self.sendError(402)

    furnitureCost = self.server.furniture.getCost(data.FurnitureId)

    if furnitureCost > self.user.Coins:
        return self.sendError(401)

    self.addFurniture(data.FurnitureId, furnitureCost)


@Handlers.Handle(XT.SaveIglooFurniture)
@Handlers.Throttle()
def handleSaveIglooFurniture(self, data):
    furnitureTracker = {}
    if len(data.FurnitureList) > 100:
        return
    for furnitureItem in set(data.FurnitureList[0:100]):
        itemArray = furnitureItem.split("|")
        if len(itemArray) > 5:
            return
        itemId, posX, posY, rotation, frame = itemArray
        itemId = int(itemId)
        if itemId not in self.furniture:
            return
        if itemId not in furnitureTracker:
            furnitureTracker[itemId] = 1
        else:
            furnitureTracker[itemId] += 1
        if furnitureTracker[itemId] > self.furniture[itemId]:
            return
        if not (0 <= int(posX) <= 700 and 0 <= int(posY) <= 700
                and 1 <= int(rotation) <= 8 and 1 <= int(frame) <= 10):
            return


@Handlers.Handle(XT.LoadPlayerIglooList)
def handleLoadPlayerIglooList(self, data):
    if len(self.server.openIgloos) == 0:
        return self.sendLine("%xt%gr%-1%")

    openIgloos = "%".join("%d|%s" % (playerId, playerName)
                      for playerId, playerName in self.server.openIgloos.items())

    self.sendXt("gr", openIgloos)

@Handlers.Handle(XT.LockIgloo)
def handleLockIgloo(self, data):
    del self.server.openIgloos[self.user.ID]


@Handlers.Handle(XT.UnlockIgloo)
def handleUnlockIgloo(self, data):
    self.server.openIgloos[self.user.ID] = self.user.Username
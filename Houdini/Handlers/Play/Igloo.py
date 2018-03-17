from beaker.cache import cache_region as Cache, region_invalidate as Invalidate

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Igloo import Igloo
@Cache("houdini", "igloo")
def getIglooString(self, penguinId):
    igloo = self.igloo if self.user.ID == penguinId else self.session.query(Igloo)\
        .filter_by(PenguinID=penguinId).first()

    if igloo is None:
        return str()

    iglooFurniture = self.session.query(IglooFurniture).join(Igloo, Igloo.PenguinID == penguinId)\
        .filter(IglooFurniture.IglooID == Igloo.ID)
    furnitureString = ",".join(["{}|{}|{}|{}|{}".format(furniture.FurnitureID, furniture.X, furniture.Y,
                                                        furniture.Rotation, furniture.Frame)
                                for furniture in iglooFurniture])

    return "%".join(map(str, [penguinId, igloo.Type, igloo.Music, igloo.Floor, furnitureString]))


@Handlers.Handle(XT.SendActivateIgloo)
def handleSendActivateIgloo(self, data):
    iglooType = data.TypeId

    if iglooType in self.igloos:
        self.igloo.Type = iglooType
        self.igloo.Floor = 0

@Handlers.Handle(XT.GetIglooDetails)
def handleGetIglooDetails(self, data):
    igloo = self.session.query(Igloo).filter_by(Owner=data.Id).first()

    if igloo is None:
        return self.transport.loseConnection()

    if data.Id == self.user.ID:
        self.igloo = igloo

    self.sendXt("gm", data.Id, igloo.Type, igloo.Music, igloo.Floor, igloo.Furniture)

# TODO: Convert owned igloos format in the database to avoid inconsistent format
@Handlers.Handle(XT.GetOwnedIgloos)
def handleGetOwnedIgloos(self, data):
    if not hasattr(self, "igloos"):
        igloos = self.user.Igloos.split("|")

        self.igloos = map(int, igloos)

    self.sendXt("go", self.user.Igloos)

@Handlers.Handle(XT.UpdateIglooMusic)
def handleUpdateIglooMusic(self, data):
    self.igloo.Music = data.MusicId

    self.session.commit()

@Handlers.Handle(XT.GetFurnitureList)
def handleGetFurnitureList(self, data):
    self.sendXt("gf", self.user.Furniture)

@Handlers.Handle(XT.UpdateFloor)
def handleUpdateFloor(self, data):
    if data.FloorId not in self.server.floors:
        return self.sendError(402)

    floorCost = self.server.floors.getCost(data.FloorId)

    if floorCost > self.user.Coins:
        return self.sendError(401)

    self.user.Coins -= floorCost
    self.igloo.Floor = data.FloorId
    self.session.commit()

    self.sendXt("ag", data.FloorId, self.user.Coins)

@Handlers.Handle(XT.UpdateIglooType)
def handleUpdateIglooType(self, data):
    if data.IglooId not in self.server.igloos:
        return self.sendError(402)

    iglooCost = self.server.igloos.getCost(data.IglooId)

    if iglooCost > self.user.Coins:
        return self.sendError(401)

    if data.IglooId in self.igloos:
        return self.sendError(500)

    self.igloos.append(data.IglooId)

    iglooIds = (str(iglooId) for iglooId in self.igloos)
    self.user.Igloos = "|".join(iglooIds)
    self.user.Coins -= iglooCost

    self.sendXt("au", data.IglooId, self.user.Coins)

@Handlers.Handle(XT.BuyFurniture)
def handleBuyFurniture(self, data):
    if data.FurnitureId not in self.server.furniture:
        return self.sendError(402)

    furnitureCost = self.server.furniture.getCost(data.FurnitureId)

    if furnitureCost > self.user.Coins:
        return self.sendError(401)

    furnitureQuantity = 1

    if data.FurnitureId in self.furniture:
        furnitureQuantity = self.furniture[data.FurnitureId]
        furnitureQuantity += 1

        if furnitureQuantity >= 100:
            return False

    self.furniture[data.FurnitureId] = furnitureQuantity

    furnitureString = "%".join("%s|%s" % (furnitureId, furnitureQuantity)
                                for furnitureId, furnitureQuantity in self.furniture.items())

    self.user.Furniture = furnitureString
    self.user.Coins -= furnitureCost
    self.session.commit()

    self.sendXt("af", data.FurnitureId, self.user.Coins)

@Handlers.Handle(XT.SaveIglooFurniture)
def handleSaveIglooFurniture(self, data):
    furnitureTracker = {}
    if len(data.FurnitureList) > 100:
        return
    for furnitureItem in data.FurnitureList[0:100]:
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
    self.igloo.Furniture = ",".join(data.FurnitureList)
    self.session.commit()

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
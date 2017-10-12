from Houdini.Handlers import Handlers, XT
from Houdini.Data.Igloo import Igloo

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

# TODO: Convert furniture id and quantity to integers?
@Handlers.Handle(XT.GetFurnitureList)
def handleGetFurnitureList(self, data):
    if not hasattr(self, "furniture"):
        self.furniture = {}

    for furnitureDetails in self.user.Furniture.split("%"):
        furnitureId, furnitureQuantity = furnitureDetails.split("|")
        self.furniture[furnitureId] = furnitureQuantity

    self.sendXt("gf", self.user.Furniture)

# TODO: Use crumbs to deduct cost and validate id
@Handlers.Handle(XT.UpdateFloor)
def handleUpdateFloor(self, data):
    try:
        floorCost = self.server.floors[data.FloorId]

        if floorCost > self.user.Coins:
            return self.sendError(401)

        self.user.Coins -= floorCost
        self.igloo.Floor = data.FloorId
        self.session.commit()

        self.sendXt("ag", data.FloorId, self.user.Coins)

    except KeyError:
        self.sendError(402)

@Handlers.Handle(XT.UpdateIglooType)
def handleUpdateIglooType(self, data):
    try:
        iglooCost = self.server.igloos[data.IglooId]

        if iglooCost > self.user.Coins:
            return self.sendError(401)

        if data.IglooId not in self.server.igloos:
            return self.sendError(402)

        if data.IglooId in self.igloos:
            return self.sendError(500)

        if data.IglooId not in self.igloos:
            self.igloos.append(data.IglooId)

        iglooIds = (str(iglooId) for iglooId in self.igloos)
        self.user.Igloos = "|".join(iglooIds)

        self.sendXt("au", data.IglooId, self.user.Coins)

    except KeyError:
        # Igloo doesn't exist
        self.sendError(402)

@Handlers.Handle(XT.BuyFurniture)
def handleBuyFurniture(self, data):
    if not hasattr(self, "furniture"):
        self.furniture = {}

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

    self.sendXt("af", data.FurnitureId, self.user.Coins)

# TODO: Validate furniture items and parameter lengths
@Handlers.Handle(XT.SaveIglooFurniture)
def handleSaveIglooFurniture(self, data):
    self.igloo.Furniture = ",".join(data.FurnitureList)

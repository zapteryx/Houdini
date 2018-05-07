import json, time
from datetime import datetime, timedelta
from beaker.cache import cache_region as Cache, region_invalidate as Invalidate
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Igloo import Igloo, IglooFurniture, IglooLike

@Cache("houdini", "igloo")
def getActiveIgloo(self, penguinId):
    igloo = self.igloo if self.user.ID == penguinId else self.session.query(Igloo) \
        .join(Penguin, Penguin.Igloo == Igloo.ID).filter(Igloo.PenguinID == penguinId).first()

    if igloo is None:
        return str()

    iglooFurniture = self.session.query(IglooFurniture).join(Igloo, Igloo.PenguinID == penguinId) \
        .filter(IglooFurniture.IglooID == igloo.ID)
    furnitureString = ",".join(["{}|{}|{}|{}|{}".format(furniture.FurnitureID, furniture.X, furniture.Y,
                                                        furniture.Rotation, furniture.Frame)
                                for furniture in iglooFurniture])

    return ":".join(map(str, [igloo.ID, 1, 0, igloo.Locked, igloo.Music, igloo.Floor, igloo.Location, igloo.Type,
                              getLayoutLikeCount(self, igloo.ID), furnitureString]))

@Cache("houdini", "igloo_layout")
def getLayoutDetails(self, layoutId):
    igloo = self.igloos[layoutId]
    slotNumber = self.igloos.index(layoutId)

    iglooFurniture = self.session.query(IglooFurniture).filter(IglooFurniture.IglooID == igloo.ID)
    furnitureString = ",".join(["{}|{}|{}|{}|{}".format(furniture.FurnitureID, furniture.X, furniture.Y,
                                                        furniture.Rotation, furniture.Frame)
                                for furniture in iglooFurniture])

    return ":".join(map(str, [igloo.ID, slotNumber, 0, igloo.Locked, igloo.Music, igloo.Floor,
                              igloo.Location, igloo.Type, getLayoutLikeCount(self, igloo.ID), furnitureString]))

# TODO: Cache layout furniture strings
@Cache("houdini", "igloo_layouts")
def getAllIglooLayouts(self, playerId):
    iglooLayouts = self.session.query(Igloo).filter_by(PenguinID=playerId)
    iglooLayoutDetails = []
    slotNumber = 0

    for igloo in iglooLayouts:
        slotNumber += 1

        iglooFurniture = self.session.query(IglooFurniture).filter(IglooFurniture.IglooID == igloo.ID)
        furnitureString = ",".join(["{}|{}|{}|{}|{}".format(furniture.FurnitureID, furniture.X, furniture.Y,
                                                            furniture.Rotation, furniture.Frame)
                                    for furniture in iglooFurniture])

        iglooLayoutDetails.append(":".join(map(str, [igloo.ID, slotNumber, 0, igloo.Locked, igloo.Music, igloo.Floor,
                                                     igloo.Location, igloo.Type, getLayoutLikeCount(self, igloo.ID),
                                                     furnitureString])))

    return "%".join(iglooLayoutDetails)

@Cache("houdini", "layout_likes")
def getLayoutLikeCount(self, layoutId):
    layoutLikeCount = self.session.query(func.sum(IglooLike.Count)).filter_by(IglooID=layoutId).scalar()
    return layoutLikeCount if layoutLikeCount is not None else 0

@Handlers.Handle(XT.BuyIglooLocation)
def handleBuyIglooLocation(self, data):
    if data.LocationId not in self.server.igloos:
        return self.sendError(402)

    locationCost = self.server.locations.getCost(data.LocationId)

    if locationCost > self.user.Coins:
        return self.sendError(401)

    if data.LocationId in self.locations:
        return self.sendError(502)

    self.addLocation(data.LocationId, locationCost)

@Handlers.Handle(XT.SetIglooManagement)
def handleSetIglooManagement(self, data):
    pass

@Handlers.Handle(XT.CanLikeIgloo)
def handleCanLikeIgloo(self, data):
    lastUpdated = self.session.query(IglooLike.Date)\
        .filter_by(IglooID=self.room.IglooId, PlayerID=self.user.ID).scalar()

    canLike = json.dumps({"canLike": True, "periodicity": "ScheduleDaily", "nextLike_msecs": 0})

    if lastUpdated is None:
        return self.sendXt("cli", self.room.IglooId, 200, canLike)

    timeElapsed = datetime.now() - lastUpdated

    if timeElapsed > timedelta(1):
        self.sendXt("cli", self.room.IglooId, 200, canLike)

    else:
        self.sendXt("cli", self.room.IglooId, 200,
                    json.dumps({"canLike": False, "periodicity": "ScheduleDaily",
                                "nextLike_msecs": (timedelta(1) - timeElapsed).total_seconds() * 1000}))

# TODO: Check if in igloo
@Handlers.Handle(XT.LikeIgloo)
@Handlers.Throttle()
def handleLikeIgloo(self, data):
    playerId = self.room.InternalId # TODO: Check if exists
    # ORM doesn't have support for ON DUPLICATE KEY as of writing this
    # Text() is necessary because ORM and Core models are incompatible
    likeInsert = insert(IglooLike).values(IglooID=self.room.IglooId,
                                          OwnerID=playerId, PlayerID=self.user.ID, Count=1)
    onDuplicateKey = likeInsert.on_duplicate_key_update(Count=IglooLike.Count + 1, Date=datetime.now())
    self.server.databaseEngine.execute(onDuplicateKey, id=playerId)

    self.session.commit()

    Invalidate(getLayoutLikeCount, "houdini", "layout_likes", self.room.IglooId)

    if len(self.room.players) > 1:
        likeCount = getLayoutLikeCount(self, self.room.IglooId)

        for player in self.room.players:
            if player.user.ID != self.user.ID:
                player.sendXt("lue", self.user.ID, likeCount)

# TODO: Maybe cache the JSON collection in a way that allows us to paginate without having to query (.all())
# TODO: Definitely cache
@Handlers.Handle(XT.GetIglooLikeBy)
def handleGetIglooLikeBy(self, data):
    # This returns a Decimal() object that must be converted into an integer type to be serialized
    likesResult = self.session.query(func.sum(IglooLike.Count))\
        .filter_by(IglooID = self.room.IglooId).scalar()

    likeCount = int(likesResult) if likesResult else 0

    likeCollection = {
        "likedby": {
            "counts": {
                "count": likeCount,
                "maxCount": likeCount,
                "accumCount": likeCount
            },
            "IDs": [
                {
                    "id": like.PlayerID,
                    "time": time.mktime(like.Date.timetuple()),
                    "count": like.Count,
                    "isFriend": False
                } for like in self.session.query(IglooLike).filter_by(IglooID=self.room.IglooId)
                    .limit(data.PaginationEnd - data.PaginationStart).offset(data.PaginationStart)
            ]
        }
    }

    self.sendXt("gili", self.room.IglooId, 200, json.dumps(likeCollection))

@Handlers.Handle(XT.IsPlayerIglooOpen)
def handleIsPlayerIglooOpen(self, data):
    self.sendXt("pio", 1 if data.Id in self.server.openIgloos else 0)

@Handlers.Handle(XT.AddIglooLayout)
def handleAddIglooLayout(self, data):
    if len(self.igloos) < 3:
        igloo = Igloo(PenguinID=self.user.ID)
        self.session.add(igloo)
        self.igloos[igloo.ID] = igloo
        self.logger.debug("Created igloo {} for {}".format(igloo.ID, self.user.ID))

        self.sendXt("al", self.user.ID, getLayoutDetails(self, igloo.ID))

# TODO: Check if they're in their igloo :thinking:
@Handlers.Handle(XT.UpdateIglooConfiguration)
def handleUpdateIglooConfiguration(self, data):
    # Checks if they're even in an igloo, and if they are.. Check if it's THEIR igloo
    if not hasattr(self.room, "IglooId") or hasattr(self.room, "IglooId") \
            and self.room.IglooId not in self.igloos:
        return self.transport.loseConnection()

    if data.LayoutId not in self.igloos:
        return self.transport.loseConnection()

    self.igloo = self.igloos[data.LayoutId]
    self.user.Igloo = data.LayoutId
    self.room.IglooId = self.igloo.ID

    furnitureTracker = {}
    furnitureList = data.FurnitureList.split(",")
    self.session.query(IglooFurniture).filter_by(IglooID=self.igloo.ID).delete()

    if len(furnitureList) > 100:
        return
    for furnitureItem in set(furnitureList[0:100]):
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
        self.session.add(IglooFurniture(IglooID=self.igloo.ID, FurnitureID=itemId, X=posX, Y=posY,
                                        Rotation=rotation, Frame=frame))

    self.igloo.Type = data.IglooId
    self.igloo.Floor = data.FloorId
    self.igloo.Location = data.LocationId
    self.igloo.Music = data.MusicId

    Invalidate(getActiveIgloo, 'houdini', 'igloo', self.user.ID)
    Invalidate(getAllIglooLayouts, 'houdini', 'igloo_layouts', self.user.ID)

    self.room.sendXt("uvi", self.user.ID, "{}:1:0:{}:{}:{}:{}:{}:{}:{}".format(self.igloo.ID, self.igloo.Locked,
                                                                               self.igloo.Music, self.igloo.Floor,
                                                                               self.igloo.Location, self.igloo.Type,
                                                                               getLayoutLikeCount(self, self.igloo.ID),
                                                                               data.FurnitureList))

@Handlers.Handle(XT.SendActivateIgloo)
def handleSendActivateIgloo(self, data):
    iglooType = data.TypeId

    if iglooType in self.igloos:
        self.igloo.Type = iglooType
        self.igloo.Floor = 0

@Handlers.Handle(XT.GetIglooDetails)
def handleGetIglooDetails(self, data):
    self.sendXt("gm", data.Id, getActiveIgloo(self, data.Id))

@Handlers.Handle(XT.GetOwnedIgloos)
def handleGetOwnedIgloos(self, data):
    self.sendXt("go", "|".join(map(str, self.igloos)))

@Handlers.Handle(XT.UpdateIglooMusic)
def handleUpdateIglooMusic(self, data):
    self.igloo.Music = data.MusicId

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

    if data.IglooId in self.iglooInventory:
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

@Handlers.Handle(XT.UpdateIglooSlotSummary)
@Handlers.Throttle()
def handleUpdateIglooSlotSummary(self, data):
    # Checks if they're even in an igloo, and if they are.. Check if it's THEIR igloo
    if not hasattr(self.room, "IglooId") or hasattr(self.room, "IglooId") \
            and self.room.IglooId not in self.igloos:
        return self.transport.loseConnection()

    if data.LayoutId not in self.igloos:
        return self.transport.loseConnection()

    self.igloo = self.igloos[data.LayoutId]
    self.user.Igloo = data.LayoutId
    self.room.IglooId = self.igloo.ID

    slotSummary = data.SlotSummary.split(",")

    for layoutSummary in slotSummary:
        layoutId, isLocked = map(int, layoutSummary.split("|"))

        if layoutId not in self.igloos:
            return self.transport.loseConnection()

        if self.igloos[layoutId].Locked != isLocked:
            self.igloos[data.LayoutId].Locked = isLocked

            if self.igloo.ID == layoutId:
                Invalidate(getActiveIgloo, 'houdini', 'igloo_details', self.user.ID)

                if bool(self.igloos[layoutId].Locked) and \
                        self.user.ID in self.server.openIgloos:
                    del self.server.openIgloos[self.user.ID]
                else:
                    self.server.openIgloos[self.user.ID] = self.user.Username

            Invalidate(getAllIglooLayouts, 'houdini', 'igloo_layouts', self.user.ID)

# TODO: Implement likes!
# TODO: Cache? (Would require invalidation on every leave/join and like submission)
@Handlers.Handle(XT.GetOpenIglooList)
def handleGetOpenIglooList(self, data):
    openIgloos = ["{}|{}|{}|{}|0".format(playerId, playerUsername, 0,
                                         len(self.server.rooms[playerId + 1000].players))
                  for playerId, playerUsername in self.server.openIgloos.items()]

    # Room population. Pretty sure this value isn't actually used xd
    localRoomPopulation = 0
    self.sendXt("gr", getLayoutLikeCount(self, self.igloo.ID), localRoomPopulation, *openIgloos)

# Even though the player's ID is sent in the packet, it is irrelevant.
@Handlers.Handle(XT.GetFurnitureInventory)
def handleGetFurnitureInventory(self, data):
    furnitureString = ",".join(["{}|0000000000|{}".format(furnitureId, quantity)
                                for furnitureId, quantity in self.furniture.items()])
    floorString = ",".join(["{}|0000000000".format(floorId) for floorId in self.floors])
    igloosString = ",".join(["{}|0000000000".format(iglooId) for iglooId in self.iglooInventory])
    locationString = ",".join(["{}|0000000000".format(locationId) for locationId in self.locations])

    self.sendXt("gii", furnitureString, floorString, igloosString, locationString)

# TODO: Cache
@Handlers.Handle(XT.GetAllIglooLayouts)
def handleGetAllIglooLayouts(self, data):
    # TODO: Consider returning igloo layout objects instead to avoid multiple queries
    self.sendXt("gail", self.user.ID, self.igloo.ID, getAllIglooLayouts(self, self.user.ID))

    totalLikes = self.session.query(func.sum(IglooLike.Count)).filter_by(OwnerID=self.user.ID).scalar()
    layoutLikes = ",".join("{}|{}".format(layoutId, likeCount) for layoutId, likeCount in
                           self.session.query(IglooLike.IglooID, func.sum(IglooLike.Count))
                           .filter_by(OwnerID=self.user.ID))
    self.sendXt("gaili", totalLikes, layoutLikes)
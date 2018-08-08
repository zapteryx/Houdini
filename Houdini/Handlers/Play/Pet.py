import time, random

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Puffle import Puffle, CareInventory
from Houdini.Data.Postcard import Postcard
from Houdini.Data import retryableTransaction

# Food Play Rest Clean
puffleStatistics = {
    0: (100, 100, 100, 100),
    1: (100, 100, 100, 100),
    2: (100, 100, 100, 100),
    3: (100, 100, 100, 100),
    4: (100, 100, 100, 100),
    5: (100, 100, 100, 100),
    6: (100, 100, 100, 100),
    7: (100, 100, 100, 100),
    8: (100, 100, 100, 100)
}

runPostcards = {
    0: 100,
    1: 101,
    2: 102,
    3: 103,
    4: 104,
    5: 105,
    6: 106,
    7: 169,
    8: 109
}

def decreaseStats(server):
    for (playerId, player) in server.players.items():
        if player.room.Id == player.user.ID + 1000:
            continue

        for (puffleId, puffle) in player.puffles.items():
            maxHealth, maxHunger, maxRest, maxClean = puffleStatistics[puffle.Type]
            if int(puffle.Walking):
                puffle.Food = max(10, min(puffle.Food - 8, maxHunger))
                puffle.Rest = max(10, min(puffle.Rest - 8, maxRest))
            else:
                puffle.Food = max(0, min(puffle.Food - 4, maxHealth))
                puffle.Food = max(0, min(puffle.Food - 4, maxHunger))
                puffle.Rest = max(0, min(puffle.Rest - 4, maxRest))

            if puffle.Food == 0 and puffle.Food == 0 and puffle.Rest == 0:
                runPostcard = runPostcards[puffle.Type]
                player.receiveSystemPostcard(runPostcard, puffle.Name)
                del player.puffles[puffle.ID]
                player.session.query(Puffle).filter_by(ID=puffle.ID).delete()
            elif puffle.Food < 10:
                notificationAware = player.session.query(Postcard).filter(Postcard.RecipientID == player.user.ID). \
                    filter(Postcard.Type == 110). \
                    filter(Postcard.Details == Puffle.Name).scalar()
                if not notificationAware:
                    player.receiveSystemPostcard(110, puffle.Name)
        handleGetMyPlayerPuffles(player, [])

def getStatistics(puffleType, puffleFood, pufflePlay, puffleRest, puffleClean):
    maxFood, maxPlay, maxRest, maxClean = puffleStatistics[puffleType]

    puffleFood = int(float(puffleFood) / maxFood * 100)
    pufflePlay = int(float(pufflePlay) / maxPlay * 100)
    puffleRest = int(float(puffleRest) / maxRest * 100)
    puffleClean = int(float(puffleClean) / maxClean * 100)

    return "{}|{}|{}|{}".format(puffleFood, pufflePlay, puffleRest, puffleClean)

@Handlers.Handle(XT.GetPlayerPuffles)
def handleGetPuffles(self, data):
    backyardBoolean = 1 if data.RoomType == "backyard" else 0
    ownedPuffles = self.session.query(Puffle).filter(Puffle.PenguinID == data.PlayerId,
                                                     Puffle.Backyard == backyardBoolean)

    playerPuffles = ["{}|{}|{}|{}|undefined|{}|{}|0|0|{}".format(puffle.ID, puffle.Type,
                                                                 puffle.Subtype if puffle.Subtype else str(),
                                                                 puffle.Name,
                                                                 getStatistics(puffle.Type, puffle.Food,
                                                                               puffle.Play, puffle.Rest,
                                                                               puffle.Clean),
                                                                 puffle.Hat, puffle.Walking)
                     for puffle in ownedPuffles]

    self.sendXt("pg", len(playerPuffles), *playerPuffles)

@Handlers.Handle(XT.GetMyPlayerPuffles)
def handleGetMyPlayerPuffles(self, data):
    playerPuffles = ["{}|{}|{}|{}|{}|{}|{}|0".format(puffle.ID, puffle.Type,
                                                     puffle.Subtype if puffle.Subtype else str(),
                                                     puffle.Name, time.mktime(puffle.AdoptionDate.timetuple()),
                                                     getStatistics(puffle.Type, puffle.Food,
                                                                   puffle.Play, puffle.Rest, puffle.Clean),
                                                     puffle.Hat)
                     for puffle in self.puffles.values()]

    self.sendXt("pgu", *playerPuffles)

@Handlers.Handle(XT.AdoptPuffle)
@retryableTransaction()
def handleSendAdoptPuffle(self, data):
    if not data.TypeId in puffleStatistics:
        return self.transport.loseConnection()

    if not 16 > len(data.Name) >= 3:
        return self.sendError(441)

    if self.user.Coins < 800:
        return self.sendError(401)

    if len(self.puffles) >= 19:
        return self.sendError(440)

    self.user.Coins -= 800

    maxFood, maxPlay, maxRest, maxClean = puffleStatistics[data.TypeId]

    puffle = Puffle(PenguinID=self.user.ID, Name=data.Name, Type=data.TypeId,
                    Subtype=data.SubtypeId, Food=maxFood, Play=maxPlay,
                    Rest=maxRest, Clean=maxClean)
    self.session.add(puffle)
    self.session.commit()

    self.puffles[puffle.ID] = puffle

    puffleString = "{}|{}|{}|{}|{}|100|100|100|100|0|0".format(puffle.ID, puffle.Type,
                                                               puffle.Subtype if data.SubtypeId else str(),
                                                               data.Name, int(time.time()))
    self.sendXt("pn", self.user.Coins, puffleString)

    self.receiveSystemPostcard(111, data.Name)

    self.addCareItem(3, 10, sendXt=False)
    self.addCareItem(79, 10, sendXt=False)

@Handlers.Handle(XT.MovePuffle)
def handleSendPuffleMove(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pm", "{}|{}|{}".format(data.PuffleId, data.X, data.Y))

@Handlers.Handle(XT.WalkPuffle)
def handleSendPuffleWalk(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        puffle.Walking = 1 if not puffle.Walking else 0
        self.walkingPuffle = puffle if puffle.Walking else None

        self.room.sendXt("pw", self.user.ID, puffle.ID, puffle.Type,
                         puffle.Subtype, puffle.Walking, puffle.Hat)

@Handlers.Handle(XT.PlayPuffle)
def handleSendPufflePlay(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest, maxClean = puffleStatistics[puffle.Type]

        negativeHunger = random.randrange(10, 25)
        negativeRest = random.randrange(10, 25)

        puffle.Food = max(0, min(puffle.Food - negativeHunger, maxHunger))
        puffle.Rest = max(0, min(puffle.Rest - negativeRest, maxRest))

        maxStatistic = max(puffle.Play, puffle.Rest)
        minStatistic = min(puffle.Play, puffle.Rest)
        puffle.Food = random.randrange(minStatistic, maxStatistic + 1)

        playType = 1 if puffle.Rest > 80 else random.choice([0, 2])

        playString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Food,
                                                                      puffle.Play, puffle.Rest,
                                                                      puffle.Clean))

        self.room.sendXt("pp", playString, playType)

@Handlers.Handle(XT.PuffleInitInteractionPlay)
def handleSendPuffleInitPlayInteraction(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pip", "{}|{}|{}".format(data.PuffleId, data.X, data.Y))

@Handlers.Handle(XT.PuffleInitInteractionRest)
def handleSendPuffleInitRestInteraction(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pir", "{}|{}|{}".format(data.PuffleId, data.X, data.Y))

@Handlers.Handle(XT.GetCareInventory)
def handleGetCareInventory(self, data):
    careInventoryString = ("{}|{}".format(careItemId, itemQuantity)
                           for (careItemId, itemQuantity) in self.careInventory.iteritems())

    self.sendXt("pgpi", *careInventoryString)

@Handlers.Handle(XT.CheckPuffleName)
def handleCheckPuffleName(self, data):
    self.sendXt("checkpufflename", data.Name, 1)

@Handlers.Handle(XT.AddPuffleCareItem)
def handleAddPuffleCareItem(self, data):
    if data.ItemId not in self.server.careItems:
        return self.sendError(402)

    itemCost = self.server.careItems.getCost(data.ItemId)

    if itemCost > self.user.Coins:
        return self.sendError(401)

    itemQuantity = self.server.careItems.getQuantity(data.ItemId)
    itemId = self.server.careItems.getRootItem(data.ItemId)

    self.addCareItem(itemId, itemQuantity, itemCost)

@Handlers.Handle(XT.GetMyPufflesStats)
def handleGetMyPufflesStats(self, data):
    puffleStats = ",".join("{}|{}|{}|{}|{}".format(puffle.ID, puffle.Food, puffle.Play,
                                                   puffle.Rest, puffle.Clean)
                           for puffle in self.puffles.values())

    self.sendXt("pgmps", puffleStats)

@Handlers.Handle(XT.GetPuffleHandlerStatus)
def handleGetPuffleHandlerStatus(self, data):
    self.sendXt("phg", 1)

@Handlers.Handle(XT.SetPuffleHanderStatus)
def handleSetPuffleHanderStatus(self, data):
    pass

@Handlers.Handle(XT.PuffleCareItemDelivered)
def handlePuffleCareItemDelivered(self, data):
    if data.PuffleId not in self.puffles:
        return self.transport.loseConnection()

    if data.CareItemId in self.careInventory:
        self.careInventory[data.CareItemId] -= 1
        if self.careInventory[data.CareItemId] < 1:
            del self.careInventory[data.CareItemId]
            self.session.query(CareInventory).filter_by(PenguinID=self.user.ID, ItemID=data.CareItemId).delete()
        else:
            self.session.query(CareInventory).filter_by(PenguinID=self.user.ID, ItemID=data.CareItemId) \
                .update({"Quantity": self.careInventory[data.CareItemId]})

    puffle = self.puffles[data.PuffleId]
    careItem = self.server.careItems.getItem(data.CareItemId)

    puffle.Food = max(0, min(puffle.Food + careItem.Effect.Food, 100))
    puffle.Play = max(0, min(puffle.Play + careItem.Effect.Play, 100))
    puffle.Rest = max(0, min(puffle.Rest + careItem.Effect.Rest, 100))
    puffle.Clean = max(0, min(puffle.Clean + careItem.Effect.Clean, 100))

    celebrationBoolean = puffle.Food == puffle.Play == puffle.Rest == puffle.Clean == 100

    careItemDelivery = "{}|{}|{}|{}|{}|{}".format(puffle.ID, puffle.Food, puffle.Play,
                                                  puffle.Rest, puffle.Clean,
                                                  int(celebrationBoolean))

    self.room.sendXt("pcid", self.user.ID, careItemDelivery)

@Handlers.Handle(XT.PuffleVisitorHatUpdate)
def handlePuffleVisitorHatUpdate(self, data):
    if data.PuffleId not in self.puffles or \
            data.HatId not in self.careInventory:
        return self.transport.loseConnection()

    self.puffles[data.PuffleId].Hat = data.HatId
    self.room.sendXt("puphi", data.PuffleId, data.HatId)

@Handlers.Handle(XT.WalkSwapPuffle)
def handleWalkSwapPuffle(self, data):
    if data.PuffleId not in self.puffles:
        return self.transport.loseConnection()

    self.walkingPuffle.Walking = 0

    puffle = self.puffles[data.PuffleId]
    puffle.Walking = 1
    self.walkingPuffle = puffle

    self.room.sendXt("pufflewalkswap", self.user.ID, puffle.ID, puffle.Type,
                     puffle.Subtype, puffle.Walking, puffle.Hat)

@Handlers.Handle(XT.PuffleTrick)
def handlePuffleTrick(self, data):
    self.room.sendXt("puffletrick", self.user.ID, data.TrickId)

@Handlers.Handle(XT.ChangePuffleRoom)
def handleChangePuffleRoom(self, data):
    if data.PuffleId not in self.puffles:
        return self.transport.loseConnection()

    puffle = self.puffles[data.PuffleId]
    puffle.Backyard = 1 if data.RoomType == "backyard" else 0
    self.room.sendXt("puffleswap", data.PuffleId, data.RoomType)
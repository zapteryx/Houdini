import time, random, json
from datetime import datetime, timedelta

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Puffle import Puffle, CareInventory, PuffleQuest
from Houdini.Data.Postcard import Postcard
from Houdini.Data import retryableTransaction

puffleTypes = range(0, 12)
puffleFavoriteFood = [101, 107, 112, 109, 110, 106, 114, 111, 108, 113, 115, 128]

def decreaseStats(server):
    for (playerId, player) in server.players.items():
        if player.room.Id == player.user.ID + 1000:
            continue

        for (puffleId, puffle) in player.puffles.items():
            if int(puffle.Walking):
                puffle.Food = max(10, min(puffle.Food - 8, 100))
                puffle.Rest = max(10, min(puffle.Rest - 8, 100))
                puffle.Clean = max(10, min(puffle.Clean - 8, 100))
            elif not puffle.Backyard:
                puffle.Food = max(0, min(puffle.Food - 4, 100))
                puffle.Play = max(0, min(puffle.Play - 4, 100))
                puffle.Rest = max(0, min(puffle.Rest - 4, 100))
                puffle.Clean = max(0, min(puffle.Clean - 4, 100))

            if puffle.Food < 10:
                notificationAware = player.session.query(Postcard).filter(Postcard.RecipientID == player.user.ID). \
                    filter(Postcard.Type == 110). \
                    filter(Postcard.Details == Puffle.Name).scalar()
                if not notificationAware:
                    player.receiveSystemPostcard(110, puffle.Name)
        handleGetMyPlayerPuffles(player, [])

@Handlers.Handle(XT.GetPlayerPuffles)
def handleGetPuffles(self, data):
    backyardBoolean = 1 if data.RoomType == "backyard" else 0
    ownedPuffles = self.session.query(Puffle).filter(Puffle.PenguinID == data.PlayerId,
                                                     Puffle.Backyard == backyardBoolean)

    playerPuffles = ["{}|{}|{}|{}|undefined|{}|{}|{}|{}|{}|0|0|{}"
                         .format(puffle.ID, puffle.Type,
                                 puffle.Subtype if puffle.Subtype else str(),
                                 puffle.Name, puffle.Food,
                                 puffle.Play, puffle.Rest, puffle.Clean,
                                 puffle.Hat, puffle.Walking)
                     for puffle in ownedPuffles]

    self.sendXt("pg", len(playerPuffles), *playerPuffles)

@Handlers.Handle(XT.GetMyPlayerPuffles)
def handleGetMyPlayerPuffles(self, data):
    playerPuffles = ["{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|0"
                         .format(puffle.ID, puffle.Type,
                                 puffle.Subtype if puffle.Subtype else str(),
                                 puffle.Name, time.mktime(puffle.AdoptionDate.timetuple()),
                                 puffle.Food, puffle.Play, puffle.Rest, puffle.Clean,
                                 puffle.Hat)
                     for puffle in self.puffles.values()]

    self.sendXt("pgu", *playerPuffles)

def handleAddInitialCareItems(self, data):
    playerPuffles = [puffle.Type for puffle in self.puffles.values()]

    if not data.SubtypeId:
        if data.TypeId == 0 and data.TypeId not in playerPuffles:
            self.addCareItem(27, 1, sendXt=False)
        elif data.TypeId == 1 and data.TypeId not in playerPuffles:
            self.addCareItem(28, 1, sendXt=False)
        elif data.TypeId == 2 and data.TypeId not in playerPuffles:
            self.addCareItem(31, 1, sendXt=False)
        elif data.TypeId == 3 and data.TypeId not in playerPuffles:
            self.addCareItem(30, 1, sendXt=False)
        elif data.TypeId == 4 and data.TypeId not in playerPuffles:
            self.addCareItem(35, 1, sendXt=False)
        elif data.TypeId == 5 and data.TypeId not in playerPuffles:
            self.addCareItem(29, 1, sendXt=False)
        elif data.TypeId == 6 and data.TypeId not in playerPuffles:
            self.addCareItem(32, 1, sendXt=False)
        elif data.TypeId == 7 and data.TypeId not in playerPuffles:
            self.addCareItem(33, 1, sendXt=False)
        elif data.TypeId == 8 and data.TypeId not in playerPuffles:
            self.addCareItem(34, 1, sendXt=False)
        elif data.TypeId == 9 and data.TypeId not in playerPuffles:
            self.addCareItem(36, 1, sendXt=False)
        elif data.TypeId == 10 and data.TypeId not in playerPuffles:
            self.addCareItem(103, 1, sendXt=False)
        elif data.TypeId == 11 and data.TypeId not in playerPuffles:
            self.addCareItem(125, 1, sendXt=False)

    if len(self.puffles) < 1:
        self.addCareItem(1, 1, sendXt=False)
        self.addCareItem(3, 10, sendXt=False)
        self.addCareItem(8, 1, sendXt=False)
        self.addCareItem(37, 1, sendXt=False)
        self.addCareItem(79, 10, sendXt=False)

@Handlers.Handle(XT.AdoptPuffle)
@retryableTransaction()
def handleSendAdoptPuffle(self, data):
    if not data.TypeId in puffleTypes:
        return self.transport.loseConnection()

    if not 16 > len(data.Name) >= 3:
        return self.sendError(441)

    if data.TypeId in range(0, 9) and not data.SubtypeId:
        puffleCost = 400
    elif data.TypeId == 10 or data.TypeId == 11 or \
             data.SubtypeId in range(1000, 1005) or \
             data.SubtypeId in range(1021, 1027):
        puffleCost = 0
    else:
        puffleCost = 800

    if self.user.Coins < puffleCost:
        return self.sendError(401)

    if len(self.puffles) >= 75 and self.user.Moderator == 0:
        return self.sendError(440)

    if data.TypeId == 10:
        questsDone = sum(1 for taskId in self.puffleQuests if
                         self.puffleQuests[taskId].Completed is not None)

        if questsDone < 4 and self.user.Moderator == 0:
            return self.transport.loseConnection()

        if self.user.Moderator == 0:
            self.user.RainbowAdoptability = 0

    if data.TypeId == 11:
        if self.user.Nuggets < 15 or not self.canDigGold:
            return self.transport.loseConnection()

        if self.user.Moderator == 0:
            self.user.Nuggets -= 15
        self.canDigGold = False

    self.user.Coins -= puffleCost

    handleAddInitialCareItems(self, data)

    puffle = Puffle(PenguinID=self.user.ID, Name=data.Name, Type=data.TypeId,
                    Subtype=data.SubtypeId)
    self.session.add(puffle)
    self.session.commit()

    self.puffles[puffle.ID] = puffle

    puffleString = "{}|{}|{}|{}|{}|100|100|100|100|0|0".format(puffle.ID, puffle.Type,
                                                               puffle.Subtype if data.SubtypeId else str(),
                                                               data.Name, int(time.time()))
    self.sendXt("pn", self.user.Coins, puffleString)

    self.receiveSystemPostcard(111, data.Name)

@Handlers.Handle(XT.MovePuffle)
def handleSendPuffleMove(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pm", "{}|{}|{}".format(data.PuffleId, data.X, data.Y))

@Handlers.Handle(XT.WalkPuffle)
def handleSendPuffleWalk(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        if not puffle.Walking:
            puffle.Walking = 1
            puffle.Backyard = 0
            self.walkingPuffle = puffle
        else:
            puffle.Walking = 0
            puffle.Backyard = 1 if self.inBackyard else 0
            self.walkingPuffle = None

        self.room.sendXt("pw", self.user.ID, puffle.ID, puffle.Type,
                         puffle.Subtype, puffle.Walking, puffle.Hat, puffle.Backyard)

@Handlers.Handle(XT.PlayPuffle)
def handleSendPufflePlay(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        negativeHunger = random.randrange(10, 25)
        negativeRest = random.randrange(10, 25)

        puffle.Food = max(0, min(puffle.Food - negativeHunger, 100))
        puffle.Rest = max(0, min(puffle.Rest - negativeRest, 100))

        puffleStats = ",".join("{}|{}|{}|{}|{}".format(puffle.ID, puffle.Food, puffle.Play,
                                                       puffle.Rest, puffle.Clean)
                               for puffle in self.puffles.values())

        self.room.sendXt("pp", puffleStats)

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

    if self.server.serverName == "Redemption":
        return self.transport.loseConnection()
    elif data.ItemId not in self.server.availableCareItems["Standard"]:
        return self.sendError(402)

    if data.ItemId not in self.careInventory:
        quantity = 0
    else:
        quantity = self.careInventory[data.ItemId]

    if self.server.careItems.getPlayExternal(data.ItemId) == "superplay":
        if quantity >= 1:
            return self.sendError(408)
    elif self.server.careItems.getType(data.ItemId) == "head":
        if quantity >= 75:
            return self.sendError(407)
    else:
        maxQuantity = self.server.careItems.getQuantity(data.ItemId)
        if quantity >= maxQuantity:
            return self.sendError(406)

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

@Handlers.Handle(XT.SetPuffleHandlerStatus)
def handleSetPuffleHandlerStatus(self, data):
    pass

@Handlers.Handle(XT.PuffleCareItemDelivered)
@Handlers.Throttle()
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

    if data.CareItemId is not puffleFavoriteFood[puffle.Type]:
        puffle.Food = max(0, min(puffle.Food + careItem.Effect.Food, 100))
        puffle.Play = max(0, min(puffle.Play + careItem.Effect.Play, 100))
        puffle.Rest = max(0, min(puffle.Rest + careItem.Effect.Rest, 100))
        puffle.Clean = max(0, min(puffle.Clean + careItem.Effect.Clean, 100))
    else:
        puffle.Food = 100
        puffle.Play = 100
        puffle.Rest = 100
        puffle.Clean = 100

    celebrationBoolean = puffle.Food == puffle.Play == puffle.Rest == puffle.Clean == 100

    careItemDelivery = "{}|{}|{}|{}|{}|{}".format(puffle.ID, puffle.Food, puffle.Play,
                                                  puffle.Rest, puffle.Clean,
                                                  int(celebrationBoolean))

    self.room.sendXt("pcid", self.user.ID, careItemDelivery)

    if data.CareItemId == 126:
        self.user.Coins -= 10 # TODO: Check if they have enough coins
        self.canDigGold = True

        self.room.sendXt("oberry", self.user.ID, puffle.ID)
        self.sendXt("currencies", "1|{}".format(self.user.Nuggets))

@Handlers.Handle(XT.PuffleVisitorHatUpdate)
def handlePuffleVisitorHatUpdate(self, data):
    if data.PuffleId not in self.puffles or \
            (data.HatId != 0 and data.HatId not in self.careInventory):
        return self.transport.loseConnection()

    self.puffles[data.PuffleId].Hat = data.HatId
    self.room.sendXt("puphi", data.PuffleId, data.HatId)

@Handlers.Handle(XT.WalkSwapPuffle)
def handleWalkSwapPuffle(self, data):
    if data.PuffleId not in self.puffles:
        return self.transport.loseConnection()

    self.walkingPuffle.Walking = 0
    self.walkingPuffle.Backyard = 1 if self.inBackyard == 1 else 0

    puffle = self.puffles[data.PuffleId]
    puffle.Walking = 1
    self.walkingPuffle = puffle

    puffle.Backyard = 0

    self.room.sendXt("pufflewalkswap", self.user.ID, puffle.ID, puffle.Type,
                     puffle.Subtype, puffle.Walking, puffle.Hat, puffle.Backyard)

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

@Handlers.Handle(XT.RainbowPuffleQuestCookie)
def handleRainbowPuffleQuestCookie(self, data):
    puffleQuests = self.puffleQuests.values()
    questsDone = sum(1 for task in puffleQuests if task.Completed is not None)
    lastQuestCompletionDate = self.session.query(PuffleQuest.Completed)\
        .order_by(PuffleQuest.Completed.desc()).first()[0]

    taskAvailability = lastQuestCompletionDate + timedelta(minutes=20) \
        if lastQuestCompletionDate is not None else datetime.now()
    minutesRemaining = (taskAvailability - datetime.now()).total_seconds() / 60

    if questsDone > 3 and minutesRemaining <= 0:
        for taskId in self.puffleQuests:
            self.puffleQuests[taskId].Completed = None
            self.puffleQuests[taskId].CoinsCollected = 0

        questsDone = 0

    taskAvailabilityUnix = time.mktime(taskAvailability.timetuple())

    tasks = {
        "currTask": next((task.TaskID for task in puffleQuests if task.Completed is None), 3),
        "taskAvail": int(taskAvailabilityUnix), # When the next task will be available
        "bonus": int(questsDone > 3 and 5220 not in self.inventory), # Sending 2 doesn't matter
        "cannon": self.user.RainbowAdoptability,
        "questsDone": questsDone,
        "hoursRemaining": 0,
        "minutesRemaining": int(minutesRemaining),
        "tasks": {
            task.TaskID: {
                "item": task.ItemCollected,
                "coin": task.CoinsCollected,
                "completed": task.Completed is not None
            }
            for task in puffleQuests
        }
    }

    self.sendXt("rpqd", json.dumps(tasks))

@Handlers.Handle(XT.RainbowPuffleTaskComplete)
def handleRainbowPuffleTaskComplete(self, data):
    if data.TaskId not in self.puffleQuests \
            or not self.walkingPuffle:
        return self.transport.loseConnection()

    lastQuestCompletionDate = self.session.query(PuffleQuest.Completed) \
        .order_by(PuffleQuest.Completed.desc()).first()[0]

    currentDatetime = datetime.now()

    if lastQuestCompletionDate is not None and \
            (currentDatetime - lastQuestCompletionDate) < timedelta(minutes=20):
        self.logger.debug("Not enough time has elapsed")
        return

    puffleTask = self.puffleQuests[data.TaskId]

    if puffleTask.Completed is not None:
        self.logger.debug("Task has already been completed!")
        return

    puffleTask.ItemCollected = 1
    puffleTask.CoinsCollected = 1
    puffleTask.Completed = currentDatetime

    if data.TaskId == 3:
        self.user.RainbowAdoptability = 1

@Handlers.Handle(XT.RainbowPuffleTaskCoinCollected)
def handleRainbowPuffleTaskCoinCollected(self, data):
    if data.TaskId not in self.puffleQuests:
        return self.transport.loseConnection()

    puffleTask = self.puffleQuests[data.TaskId]

    # User has already collected coins
    if puffleTask.CoinsCollected == 2:
        return self.transport.loseConnection()

    puffleTask.CoinsCollected = 2

    self.user.Coins += (data.TaskId + 1) * 50
    self.sendXt("rpqcc", data.TaskId, 2, self.user.Coins)

@Handlers.Handle(XT.RainbowPuffleTaskItemCollected)
def handleRainbowPuffleTaskItemCollected(self, data):
    if data.TaskId not in self.puffleQuests:
        return self.transport.loseConnection()

    puffleTask = self.puffleQuests[data.TaskId]

    if puffleTask.ItemCollected == 2:
        return self.transport.loseConnection()

    taskItems = (6158, 4809, 1560, 3159)

    self.addItem(taskItems[data.TaskId], sendXt=False)

    puffleTask.ItemCollected = 2
    self.sendXt("rpqic", data.TaskId, 2)

@Handlers.Handle(XT.RainbowPuffleTaskBonusCollected)
def handleRainbowPuffleTaskBonusCollected(self, data):
    if not self.puffleQuests[3].Completed:
        return self.transport.loseConnection()

    self.user.Coins += 500
    self.addItem(5220)
    # We don't respond with the packet because it's broken

@Handlers.Handle(XT.RainbowPuffleCheckName)
def handleRainbowPuffleCheckName(self, data):
    self.sendXt("pcn")

@Handlers.Handle(XT.PuffleFrame)
def handlePuffleFrame(self, data):
    self.sendXt("ps", data.PuffleId, data.FrameId)

def selectTreasureByType(self, treasureType):
    goldenItems = self.walkingPuffle.Type == 11
    borderTabbyItems = self.walkingPuffle.Subtype in (1006, 1007)
    if treasureType == "Food":
        careItemId = random.choice(puffleFavoriteFood)
        self.addCareItem(careItemId, sendXt=False)
        if careItemId == puffleFavoriteFood[self.walkingPuffle.Type]:
            self.addStamp(495, sendXt=True)
        return careItemId, 1
    elif treasureType == "Furniture":
        furnitureList = self.server.config["Treasure"]["Furniture"]
        if goldenItems:
            furnitureList.extend(self.server.config["Treasure"]["Gold"]["Furniture"])
        if borderTabbyItems:
            furnitureList.extend(self.server.config["Treasure"]["BorderTabby"]["Furniture"])
        furnitureId = random.choice(furnitureList)
        self.addFurniture(furnitureId, sendXt=False)
        return furnitureId, 1
    elif treasureType == "Clothing":
        self.addStamp(494, True)
        clothingList = self.server.config["Treasure"]["Clothing"]

        if goldenItems:
            clothingList.extend(self.server.config["Treasure"]["Gold"]["Clothing"])
        if borderTabbyItems:
            clothingList.extend(self.server.config["Treasure"]["BorderTabby"]["Clothing"])

        availableClothing = list(set(clothingList) - set(self.inventory))

        if not availableClothing:
            treasureQuantity = random.randrange(10, 250)
            self.user.Coins += treasureQuantity
            if treasureQuantity >= 50:
                self.addStamp(493, True)
            return 0, treasureQuantity

        itemId = random.choice(availableClothing)
        self.addItem(itemId, sendXt=False)
        return itemId, 1

@Handlers.Handle(XT.PuffleTreasure)
@Handlers.Throttle(5)
def handlePuffleTreasure(self, data, digOnCommand=False):
    if not self.walkingPuffle:
        return self.transport.loseConnection()

    treasureTypes = {0: "Coins", 1: "Food", 2: "Furniture", 3: "Clothing", None: None}

    if self.canDigGold:
        treasureTypes[4] = "Gold"
        del treasureTypes[1], treasureTypes[2], \
            treasureTypes[3], treasureTypes[None]

    if digOnCommand and None in treasureTypes:
        del treasureTypes[None]

    treasureTypeIndex = random.choice(list(treasureTypes))
    treasureType = treasureTypes[treasureTypeIndex]

    if treasureType is None:
        return self.room.sendXt("nodig", self.user.ID, 1)
    elif treasureTypeIndex == 0: # Coins
        treasureId = 0
        treasureQuantity = random.randrange(10, 250)
        self.user.Coins += treasureQuantity
        if treasureQuantity >= 50:
            self.addStamp(493, True)
    elif treasureTypeIndex == 4 and self.canDigGold and self.user.Nuggets < 15:
        # Dig golden nuggets
        treasureId = 0
        treasureQuantity = random.randrange(1, 4)

        self.user.Nuggets += treasureQuantity
        self.sendXt("currencies", "1|{}".format(self.user.Nuggets))
    else:
        treasureId, treasureQuantity = selectTreasureByType(self, treasureType)

    firstSuccessfulDig = self.user.HasDug == 0

    if firstSuccessfulDig:
        self.addStamp(489, True)

        for player in self.room.players:
            player.addStamp(490, True)

    self.room.sendXt("puffledig", self.user.ID, self.walkingPuffle.ID,
                     treasureTypeIndex, treasureId, treasureQuantity,
                     int(firstSuccessfulDig))
    self.user.HasDug = 1
    self.walkingPuffle.HasDug = 1
    self.digCount += 1

    if self.digCount == 5:
        self.addStamp(492, True)

    pufflesHaveDug = set([self.puffles[puffleId].Type
                          for puffleId in self.puffles
                          if self.puffles[puffleId].HasDug])

    if pufflesHaveDug == set(puffleTypes):
        self.addStamp(491, True)

@Handlers.Handle(XT.PuffleTreasureOnCommand)
@Handlers.Throttle(120)
def handlePuffleTreasureOnCommand(self, data):
    handlePuffleTreasure(self, [], digOnCommand=True)

@Handlers.Handle(XT.PenguinOnSlideOrZipline)
def handlePenguinOnSlideOrZipline(self, data):
    self.room.sendXt("followpath", self.user.ID, data.ServerId)

@Handlers.Handle(XT.GoldRevealAnimation)
def handleGoldRevealAnimation(self, data):
    if not self.canDigGold or not self.user.Nuggets >= 15:
        return self.transport.loseConnection()

    self.room.sendXt("revealgoldpuffle", self.user.ID)

@Handlers.Handle(XT.CareStationMenu)
def handleCareStationMenu(self, data):
    self.sendXt("carestationmenu", "121|117", "119")

@Handlers.Handle(XT.CareStationMenuChoice)
def handleCareStationMenuChoice(self, data):

    data.PuffleId = self.walkingPuffle.ID
    puffle = self.puffles[data.PuffleId]

    itemCost = 5 if data.ItemChosen == 121 else 10

    if self.user.Coins >= itemCost:
        self.user.Coins -= itemCost

        if data.ItemChosen == 121:
            puffle.Food = max(0, min(puffle.Food + 30, 100))
            puffle.Play = max(0, min(puffle.Play + -10, 100))
            puffle.Rest = max(0, min(puffle.Rest + -8, 100))
            puffle.Clean = max(0, min(puffle.Clean + -1, 100))
        else:
            puffle.Food = max(0, min(puffle.Food + 100, 100))

        self.sendXt("carestationmenuchoice", self.user.ID, puffle.Food, puffle.Play, puffle.Rest, puffle.Clean)
    else:
        return self.sendError(401)

@Handlers.Handle(XT.ReturnPuffle)
def handleReturnPuffle(self, data):
    if data.PuffleId not in self.puffles:
        return self.transport.loseConnection()

    del self.puffles[data.PuffleId]

    if self.walkingPuffle is not None and \
            self.walkingPuffle.ID == data.PuffleId:
        self.walkingPuffle = None

    self.session.query(Puffle).filter(Puffle.ID == data.PuffleId).delete()
    self.session.commit()

    self.room.sendXt("prp", data.PuffleId)

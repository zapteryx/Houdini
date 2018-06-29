import random

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Puffle import Puffle, PuffleRowProxy
from Houdini.Data.Postcard import Postcard

from twisted.internet.defer import inlineCallbacks, returnValue

puffleStatistics = {
    0: (100, 100, 100),
    1: (100, 120, 80),
    2: (120, 80, 100),
    3: (80, 100, 120),
    4: (80, 120, 80),
    5: (100, 80, 120),
    6: (100, 100, 100),
    7: (120, 80, 100),
    8: (100, 80, 120)
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

@inlineCallbacks
def decreaseStats(server):
    wildPuffleIds = []
    for (playerId, player) in server.players.items():
        if player.room.Id == player.user.ID + 1000:
            continue

        for (puffleId, puffle) in player.puffles.items():
            maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]
            if int(puffle.Walking):
                puffle.Hunger = max(10, min(puffle.Hunger - 8, maxHunger))
                puffle.Rest = max(10, min(puffle.Rest - 8, maxRest))
            else:
                puffle.Health = max(0, min(puffle.Health - 4, maxHealth))
                puffle.Hunger = max(0, min(puffle.Hunger - 4, maxHunger))
                puffle.Rest = max(0, min(puffle.Rest - 4, maxRest))

            if puffle.Health == 0 and puffle.Hunger == 0 and puffle.Rest == 0:
                runPostcard = runPostcards[puffle.Type]
                player.receiveSystemPostcard(runPostcard, puffle.Name)
                del player.puffles[puffle.ID]
                wildPuffleIds.append(puffle.ID)
            elif puffle.Hunger < 10:
                result = yield server.databaseEngine.execute(
                    Postcard.select((Postcard.c.RecipientID == player.user.ID) & (Postcard.c.Type == 110) &
                                    (Postcard.c.Details == puffle.Name)))
                notificationAware = yield result.scalar()
                if not notificationAware:
                    player.receiveSystemPostcard(110, puffle.Name)
        handleGetMyPlayerPuffles(player, [])
    server.databaseEngine.execute(Puffle.delete().where(Puffle.c.ID.in_(wildPuffleIds)))

def getStatistics(puffleType, puffleHealth, puffleHunger, puffleRest):
    maxHealth, maxHunger, maxRest = puffleStatistics[puffleType]
    puffleHealth = int(float(puffleHealth) / maxHealth * 100)
    puffleRest = int(float(puffleRest) / maxRest * 100)
    puffleHunger = int(float(puffleHunger) / maxHunger * 100)
    return "{}|{}|{}".format(puffleHealth, puffleHunger, puffleRest)

@Handlers.Handle(XT.GetPlayerPuffles)
@inlineCallbacks
def handleGetPuffles(self, data):
    ownedPuffles = yield self.engine.fetchall(Puffle.select(Puffle.c.PenguinID == data.PlayerId))
    playerPuffles = ["{}|{}|{}|{}|100|100|100|0|0|0|{}".format(puffle.ID, puffle.Name, puffle.Type,
                                                               getStatistics(puffle.Type, puffle.Health,
                                                                             puffle.Hunger, puffle.Rest), puffle.Walking)
                     for puffle in ownedPuffles]

    playerPufflesString = "%".join(playerPuffles)

    self.sendXt("pg", playerPufflesString)

@Handlers.Handle(XT.GetMyPlayerPuffles)
def handleGetMyPlayerPuffles(self, data):
    playerPuffles = ["{}|{}|{}|{}|100|100|100".format(puffle.ID, puffle.Name, puffle.Type,
                                                      getStatistics(puffle.Type, puffle.Health,
                                                                    puffle.Hunger, puffle.Rest))
                     for puffle in self.puffles.values()]

    myPufflesString = "%".join(playerPuffles)

    self.sendXt("pgu", myPufflesString)

@Handlers.Handle(XT.AdoptPuffle)
@inlineCallbacks
def handleSendAdoptPuffle(self, data):
    if not data.TypeId in puffleStatistics:
        returnValue(self.transport.loseConnection())

    if not 16 > len(data.Name) >= 3:
        returnValue(self.sendError(441))

    if self.user.Coins < 800:
        returnValue(self.sendError(401))

    if len(self.puffles) >= 19:
        returnValue(self.sendError(440))

    self.user.Coins -= 800

    maxHealth, maxHunger, maxRest = puffleStatistics[data.TypeId]

    result = yield self.engine.execute(Puffle.insert(),
        PenguinID=self.user.ID, Name=data.Name, Type=data.TypeId,
        Health=maxHealth, Hunger=maxHunger, Rest=maxRest)
    puffle = yield self.engine.first(Puffle.select(Puffle.c.ID == result.inserted_primary_key[0]))
    self.puffles[puffle.ID] = PuffleRowProxy(self.engine, puffle)

    puffleString = "{}|{}|{}|100|100|100|100|100|100".format(puffle.ID, data.Name, data.TypeId)
    self.sendXt("pn", self.user.Coins, puffleString)

    self.receiveSystemPostcard(111, data.Name)

    # Refresh my player puffles
    handleGetMyPlayerPuffles(self, [])

@Handlers.Handle(XT.MovePuffle)
def handleSendPuffleMove(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pm", data.PuffleId, data.X, data.Y)

@Handlers.Handle(XT.WalkPuffle)
def handleSendPuffleWalk(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]
        if puffle.Rest < 20 and puffle.Hunger < 40:
            return # Client shouldn't have been allowed to send this packet

        puffle.Walking = 1 if not puffle.Walking else 0

        # Blame Club Penguin and not me!
        puffleData = [data.PuffleId]
        puffleData[1:11] = [''] * 11
        puffleData.append(puffle.Walking)

        puffleString = "|".join([str(puffleElement) for puffleElement in puffleData])

        self.room.sendXt("pw", self.user.ID, puffleString)

@Handlers.Handle(XT.PlayPuffle)
def handleSendPufflePlay(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        if puffle.Rest < 20 or puffle.Health < 10:
            return  # Client shouldn't have been allowed to send this packet

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        negativeHunger = random.randrange(10, 25)
        negativeRest = random.randrange(10, 25)

        puffle.Hunger = max(0, min(puffle.Hunger - negativeHunger, maxHunger))
        puffle.Rest = max(0, min(puffle.Rest - negativeRest, maxRest))

        maxStatistic = max(puffle.Hunger, puffle.Rest)
        minStatistic = min(puffle.Hunger, puffle.Rest)
        puffle.Health = random.randrange(minStatistic, maxStatistic + 1)

        playType = 1 if puffle.Rest > 80 else random.choice([0, 2])

        playString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("pp", playString, playType)

@Handlers.Handle(XT.RestPuffle)
def handleSendPuffleRest(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalHunger = random.randrange(5, 25)
        additionalRest = random.randrange(10, 25)

        puffle.Hunger = max(0, min(puffle.Hunger + additionalHunger, maxHunger))
        puffle.Rest = max(0, min(puffle.Rest + additionalRest, maxRest))

        maxStatistic = max(puffle.Hunger, puffle.Rest)
        minStatistic = min(puffle.Hunger, puffle.Rest)
        puffle.Health = random.randrange(minStatistic, maxStatistic + 1)

        restString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("pr", restString)

# TODO: Consider writing reusable functions for these handlers..?
@Handlers.Handle(XT.TreatPuffle)
def handleSendPuffleTreat(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalHunger = random.randrange(5, 15)
        puffle.Hunger = max(0, min(puffle.Hunger + additionalHunger, maxHunger))

        self.user.Coins -= 5

        treatString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                       puffle.Hunger, puffle.Rest))

        self.room.sendXt("pt", self.user.Coins, treatString, data.TreatId)

@Handlers.Handle(XT.FeedPuffle)
def handleSendPuffleFood(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalHunger = random.randrange(5, 15)
        puffle.Hunger = max(0, min(puffle.Hunger + additionalHunger, maxHunger))

        self.user.Coins -= 10

        feedString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("pf", self.user.Coins, feedString)

@Handlers.Handle(XT.BathPuffle)
def handleSendPuffleBath(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalRest = random.randrange(5, 15)
        additionalHealth = random.randrange(5, 15)
        puffle.Rest = max(0, min(puffle.Rest + additionalRest, maxRest))
        puffle.Health = max(0, min(puffle.Health + additionalHealth, maxHealth))
        self.user.Coins -= 5

        bathString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("pb", self.user.Coins, bathString)

@Handlers.Handle(XT.PuffleInitInteractionPlay)
def handleSendPuffleInitPlayInteraction(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pip", data.PuffleId, data.X, data.Y)

@Handlers.Handle(XT.PuffleInitInteractionRest)
def handleSendPuffleInitRestInteraction(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pir", data.PuffleId, data.X, data.Y)

@Handlers.Handle(XT.InteractionPlay)
def handleSendPlayInteraction(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        if puffle.Rest < 20 or puffle.Health < 10:
            return  # Client shouldn't have been allowed to send this packet

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        negativeHunger = random.randrange(10, 25)
        negativeRest = random.randrange(10, 25)

        puffle.Hunger = max(0, min(puffle.Hunger - negativeHunger, maxHunger))
        puffle.Rest = max(0, min(puffle.Rest - negativeRest, maxRest))

        maxStatistic = max(puffle.Hunger, puffle.Rest)
        minStatistic = min(puffle.Hunger, puffle.Rest)
        puffle.Health = random.randrange(minStatistic, maxStatistic + 1)

        playString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("ip", playString, data.X, data.Y)

@Handlers.Handle(XT.InteractionRest)
def handleSendRestInteraction(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalHunger = random.randrange(5, 25)
        additionalRest = random.randrange(10, 25)

        puffle.Hunger = max(0, min(puffle.Hunger + additionalHunger, maxHunger))
        puffle.Rest = max(0, min(puffle.Rest + additionalRest, maxRest))

        maxStatistic = max(puffle.Hunger, puffle.Rest)
        minStatistic = min(puffle.Hunger, puffle.Rest)
        puffle.Health = random.randrange(minStatistic, maxStatistic + 1)

        restString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("ir", restString, data.X, data.Y)

@Handlers.Handle(XT.InteractionFeed)
def handleSendFeedInteraction(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        maxHealth, maxHunger, maxRest = puffleStatistics[puffle.Type]

        additionalHunger = random.randrange(5, 15)
        puffle.Hunger = max(0, min(puffle.Hunger + additionalHunger, maxHunger))

        self.user.Coins -= 10

        feedString = "{}|Hou|dini|{}".format(puffle.ID, getStatistics(puffle.Type, puffle.Health,
                                                                      puffle.Hunger, puffle.Rest))

        self.room.sendXt("if", self.user.Coins, feedString, data.X, data.Y)

@Handlers.Handle(XT.PuffleFrame)
def handleSendPuffleFrame(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("ps", data.PuffleId, data.FrameId)
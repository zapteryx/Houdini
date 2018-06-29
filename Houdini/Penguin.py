import time

from Houdini.Spheniscidae import Spheniscidae
from Houdini.Data.Penguin import Inventory, IglooInventory, FurnitureInventory
from Houdini.Data.Puffle import Puffle
from Houdini.Data.Postcard import Postcard
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Deck import Deck
from Houdini.Data.Login import Login

from Houdini.Handlers.Games.Table import leaveTable
from Houdini.Handlers.Games.Waddle import leaveWaddle
from Houdini.Handlers.Play.Stampbook import getStampsString
from Houdini.Handlers.Play.Item import rankAwards, beltPostcards, beltStamps

from twisted.internet.defer import inlineCallbacks
from twisted.internet import threads

from sqlalchemy.sql import select


class Penguin(Spheniscidae):

    def __init__(self, engine, spirit):
        super(Penguin, self).__init__(engine, spirit)
        self.user = None
        self.throttle = {}

        self.frame = 1
        self.x, self.y = (0, 0)
        self.age = 0
        self.muted = False
        self.playerString = None

        self.table = None
        self.waddle = None
        self.gameFinished = True

        self.logger.info("Penguin class instantiated")

    def addItem(self, itemId, itemCost=0, sendXt=True):
        if itemId in self.inventory:
            return False

        self.inventory.append(itemId)
        self.engine.execute(Inventory.insert(), PenguinID=self.user.ID, ItemID=itemId)

        self.user.Coins -= itemCost

        if sendXt:
            self.sendXt("ai", itemId, self.user.Coins)

    def addIgloo(self, iglooId, iglooCost=0):
        if iglooId in self.igloos:
            return False

        self.igloos.append(iglooId)
        self.engine.execute(IglooInventory.insert(), PenguinID=self.user.ID, IglooID=iglooId)

        self.user.Coins -= iglooCost

        self.sendXt("au", iglooId, self.user.Coins)

    def addFurniture(self, furnitureId, furnitureCost=0):
        furnitureQuantity = 1

        if furnitureId in self.furniture:
            furnitureQuantity = self.furniture[furnitureId]
            furnitureQuantity += 1

            if furnitureQuantity >= 100:
                return False

            self.engine.execute(FurnitureInventory.update(
                (FurnitureInventory.c.PenguinID == self.user.ID) & (FurnitureInventory.c.FurnitureID == furnitureId))
                                .values(Quantity=furnitureQuantity))
        else:
            self.engine.execute(FurnitureInventory.insert(), PenguinID=self.user.ID, FurnitureID=furnitureId)

        self.furniture[furnitureId] = furnitureQuantity
        self.user.Coins -= furnitureCost

        self.sendXt("af", furnitureId, self.user.Coins)

    def addFlooring(self, floorId, floorCost=0):
        self.user.Coins -= floorCost
        self.igloo.Floor = floorId

        self.sendXt("ag", floorId, self.user.Coins)

    def addStamp(self, stampId, sendXt=False):
        if stampId in self.stamps:
            return False

        self.stamps.append(stampId)
        self.recentStamps.append(stampId)
        self.engine.execute(Stamp.insert(), PenguinID=self.user.ID, Stamp=stampId)

        if sendXt:
            self.sendXt("aabs", stampId)

        getStampsString.invalidate(self, self.user.ID)

    def addCards(self, *args):
        for cardId in args:
            cardQuantity = 1

            if cardId in self.deck:
                cardQuantity = self.deck[cardId]
                cardQuantity += 1

                self.engine.execute(Deck.update(
                    (Deck.c.PenguinID == self.user.ID) & (Deck.c.CardID == cardId))
                                    .values(Quantity=cardQuantity))
            else:
                self.engine.execute(Deck.insert(), PenguinID=self.user.ID, CardID=cardId)

            self.deck[cardId] = cardQuantity
            self.cards.append(self.server.cards[cardId])

    def ninjaRankUp(self, levels=1):
        for i in xrange(levels):
            if self.user.NinjaRank == 10:
                return False
            self.user.NinjaRank += 1
            self.user.NinjaProgress = 0
            self.addItem(rankAwards[self.user.NinjaRank - 1], sendXt=False)
            if self.user.NinjaRank in beltPostcards:
                self.receiveSystemPostcard(beltPostcards[self.user.NinjaRank])
            if self.user.NinjaRank in beltStamps:
                self.addStamp(beltStamps[self.user.NinjaRank], True)

    def joinRoom(self, roomId):
        self.room.remove(self)
        self.server.rooms[roomId].add(self)

    def sendCoins(self, coinAmount):
        self.user.Coins = coinAmount
        self.sendXt("zo", self.user.Coins, "", 0, 0, 0)

    def getPlayerString(self):
        playerArray = (
            self.user.ID,
            self.user.Nickname,
            self.user.Approval,
            self.user.Color,
            self.user.Head,
            self.user.Face,
            self.user.Neck,
            self.user.Body,
            self.user.Hand,
            self.user.Feet,
            self.user.Flag,
            self.user.Photo,
            self.x, self.y,
            self.frame,
            1, self.age
        )

        playerStringArray = map(str, playerArray)
        self.playerString = "|".join(playerStringArray)

        return self.playerString

    @inlineCallbacks
    def receiveSystemPostcard(self, postcardId, details=""):
        result = yield self.engine.execute(Postcard.insert(), RecipientID=self.user.ID,
                                           SenderID=None, Details=details, Type=postcardId)
        self.sendXt("mr", "sys", 0, postcardId, details, int(time.time()), result.inserted_primary_key[0])

    @inlineCallbacks
    def connectionLost(self, reason):
        if hasattr(self, "room") and self.room is not None:
            self.room.remove(self)
            puffleId = yield self.engine.scalar(select([Puffle.c.ID]).where((Puffle.c.PenguinID == self.user.ID)
                                                                           & (Puffle.c.Walking == 1)))

            if puffleId is not None:
                self.user.Hand = 0
                self.engine.execute(Puffle.update(Puffle.c.ID == puffleId).values(Walking=0))

            for buddyId in self.buddies.keys():
                if buddyId in self.server.players:
                    self.server.players[buddyId].sendXt("bof", self.user.ID)

            loginDate, ipAddr = self.login
            loginUnix = time.mktime(loginDate.timetuple())
            minutesPlayed = int(time.time() - loginUnix) / 60
            self.user.MinutesPlayed += minutesPlayed

            self.engine.execute(Login.insert(), PenguinID=self.user.ID, Date=loginDate, IPAddress=ipAddr)

            threads.deferToThread(self.server.redis.srem, "{}.players".format(self.server.serverName), self.user.ID)
            threads.deferToThread(self.server.redis.decr, "{}.population".format(self.server.serverName))


        super(Penguin, self).connectionLost(reason)

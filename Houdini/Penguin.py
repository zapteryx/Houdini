import time

from Houdini.Spheniscidae import Spheniscidae
from Houdini.Data.Penguin import Inventory, IglooInventory, FurnitureInventory
from Houdini.Data.Puffle import Puffle
from Houdini.Data.Postcard import Postcard
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Deck import Deck

from Houdini.Handlers.Games.Table import leaveTable
from Houdini.Handlers.Games.Waddle import leaveWaddle
from Houdini.Handlers.Play.Stampbook import getStampsString
from Houdini.Handlers.Play.Item import rankAwards, beltPostcards, beltStamps


class Penguin(Spheniscidae):

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

        self.user.Coins -= itemCost

        if sendXt:
            self.sendXt("ai", itemId, self.user.Coins)

    def addIgloo(self, iglooId, iglooCost=0):
        if iglooId in self.igloos:
            return False

        self.igloos.append(iglooId)
        self.user.Coins -= iglooCost

        self.sendXt("au", iglooId, self.user.Coins)

    def addFurniture(self, furnitureId, furnitureCost=0):
        furnitureQuantity = 1

        if furnitureId in self.furniture:
            furnitureQuantity = self.furniture[furnitureId]
            furnitureQuantity += 1

            if furnitureQuantity >= 100:
                return False

        else:

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

        if sendXt:
            self.sendXt("aabs", stampId)

    def addCards(self, *args):
        for cardId in args:
            cardQuantity = 1

            if cardId in self.deck:
                cardQuantity = self.deck[cardId]
                cardQuantity += 1

            else:

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

    def receiveSystemPostcard(self, postcardId, details=""):
        self.sendXt("mr", "sys", 0, postcardId, details, int(time.time()), postcard.ID)

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

    def connectionLost(self, reason):
        if hasattr(self, "room") and self.room is not None:
            self.room.remove(self)

            if puffleId is not None:
                self.user.Hand = 0

            for buddyId in self.buddies.keys():
                if buddyId in self.server.players:
                    self.server.players[buddyId].sendXt("bof", self.user.ID)

            minutesPlayed = int(time.time() - loginUnix) / 60
            self.user.MinutesPlayed += minutesPlayed

            self.server.redis.srem("%s.players" % self.server.serverName, self.user.ID)
            self.server.redis.decr("%s.population" % self.server.serverName)

        super(Penguin, self).connectionLost(reason)

import time
from beaker.cache import region_invalidate as Invalidate

from Houdini.Spheniscidae import Spheniscidae
from Houdini.Data.Penguin import Inventory, IglooInventory, FurnitureInventory, LocationInventory
from Houdini.Data.Puffle import Puffle
from Houdini.Data.Postcard import Postcard
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Deck import Deck
from Houdini.Data import retryableTransaction

from Houdini.Handlers.Games.Table import leaveTable
from Houdini.Handlers.Games.Waddle import leaveWaddle
from Houdini.Handlers.Play.Stampbook import getStampsString


class Penguin(Spheniscidae):

    def __init__(self, session, spirit):
        super(Penguin, self).__init__(session, spirit)
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
        self.session.add(Inventory(PenguinID=self.user.ID, ItemID=itemId))

        self.user.Coins -= itemCost

        if sendXt:
            self.sendXt("ai", itemId, self.user.Coins)

    def addIgloo(self, iglooId, iglooCost=0):
        if iglooId in self.iglooInventory:
            return False

        self.iglooInventory.append(iglooId)
        self.session.add(IglooInventory(PenguinID=self.user.ID, IglooID=iglooId))
        self.user.Coins -= iglooCost

        self.sendXt("au", iglooId, self.user.Coins)

    def addLocation(self, locationId, locationCost=0):
        if locationId in self.locations:
            return False

        self.iglooInventory.append(locationId)
        self.session.add(LocationInventory(PenguinID=self.user.ID, LocationID=locationId))
        self.user.Coins -= locationCost

        self.sendXt("aloc", locationId, self.user.Coins)

    def addFurniture(self, furnitureId, furnitureCost=0):
        furnitureQuantity = 1

        if furnitureId in self.furniture:
            furnitureQuantity = self.furniture[furnitureId]
            furnitureQuantity += 1

            if furnitureQuantity >= 100:
                return False

            self.session.query(FurnitureInventory).filter_by(PenguinID=self.user.ID, FurnitureID=furnitureId) \
                .update({"Quantity": furnitureQuantity})
        else:
            self.session.add(FurnitureInventory(PenguinID=self.user.ID, FurnitureID=furnitureId))

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
        self.session.add(Stamp(PenguinID=self.user.ID, Stamp=stampId))

        if sendXt:
            self.sendXt("aabs", stampId)
        Invalidate(getStampsString, 'houdini', 'stamps', self.user.ID)

    def addCards(self, *args):
        for cardId in args:
            cardQuantity = 1

            if cardId in self.deck:
                cardQuantity = self.deck[cardId]
                cardQuantity += 1

                self.session.query(Deck).filter_by(PenguinID=self.user.ID, CardID=cardId) \
                    .update({"Quantity": cardQuantity})
            else:
                self.session.add(Deck(PenguinID=self.user.ID, CardID=cardId))

            self.deck[cardId] = cardQuantity
            self.cards.append(self.server.cards[cardId])

    def ninjaRankUp(self, levels=1):
        rankAwards = [4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 104]
        beltPostcards = {1: 177, 5: 178, 9: 179}
        beltStamps = {1: 230, 5: 232, 9: 234, 10: 236}
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

    @retryableTransaction()
    def receiveSystemPostcard(self, postcardId, details=""):
        postcard = Postcard(RecipientID=self.user.ID, SenderID=None, Details=details, Type=postcardId)
        self.session.add(postcard)
        self.session.commit()
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
            self.user.Member,
            self.user.MembershipDays,
            self.user.Avatar
        )

        playerStringArray = map(str, playerArray)
        self.playerString = "|".join(playerStringArray)

        return self.playerString

    def connectionLost(self, reason):
        if hasattr(self, "room") and self.room is not None:
            self.room.remove(self)

            puffleId = self.session.query(Puffle.ID) \
                .filter(Puffle.PenguinID == self.user.ID, Puffle.Walking == 1).scalar()

            if puffleId is not None:
                self.user.Hand = 0
                self.session.query(Puffle.ID == puffleId).update({"Walking": 0})

            for buddyId in self.buddies.keys():
                if buddyId in self.server.players:
                    self.server.players[buddyId].sendXt("bof", self.user.ID)

            loginUnix = time.mktime(self.login.Date.timetuple())
            minutesPlayed = int(time.time() - loginUnix) / 60
            self.user.MinutesPlayed += minutesPlayed
            self.session.add(self.login)

            self.server.redis.srem("%s.players" % self.server.serverName, self.user.ID)
            self.server.redis.decr("%s.population" % self.server.serverName)

        super(Penguin, self).connectionLost(reason)
        # After the data has been committed; to ensure that the data was saved.
        map(self.session.expunge, self.igloos.values())

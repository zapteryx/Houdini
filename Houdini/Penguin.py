import time
from beaker.cache import region_invalidate as Invalidate

from Houdini.Spheniscidae import Spheniscidae
from Houdini.Data.Penguin import Inventory, IglooInventory, FurnitureInventory, LocationInventory, FloorInventory, BuddyList
from Houdini.Data.Puffle import Puffle, CareInventory
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

        self.walkingPuffle = None
        self.digCount = 0
        self.canDigGold = False

        self.logger.info("Penguin class instantiated")

    def addCareItem(self, careItemId, additionalQuantity=1, itemCost=0, sendXt=True):
        if careItemId in self.careInventory:
            itemQuantity = self.careInventory[careItemId]
            itemQuantity += additionalQuantity

            self.session.query(CareInventory).filter_by(PenguinID=self.user.ID, ItemID=careItemId) \
                .update({"Quantity": itemQuantity})
        else:
            itemQuantity = additionalQuantity
            self.session.add(CareInventory(PenguinID=self.user.ID, ItemID=careItemId, Quantity=additionalQuantity))

        self.careInventory[careItemId] = itemQuantity
        self.user.Coins -= itemCost

        if sendXt:
            self.sendXt("papi", self.user.Coins, careItemId, itemQuantity)

    def addItem(self, itemId, itemCost=0, sendXt=True):
        if itemId in self.inventory:
            return False

        self.inventory.append(itemId)
        self.session.add(Inventory(PenguinID=self.user.ID, ItemID=itemId))

        self.user.Coins -= itemCost

        if sendXt:
            self.sendXt("ai", itemId, self.user.Coins)

    def addIgloo(self, iglooId, iglooCost=0, sendXt=True):
        if iglooId in self.iglooInventory:
            return False

        self.iglooInventory.append(iglooId)
        self.session.add(IglooInventory(PenguinID=self.user.ID, IglooID=iglooId))
        self.user.Coins -= iglooCost

        if sendXt:
            self.sendXt("au", iglooId, self.user.Coins)

    def addLocation(self, locationId, locationCost=0, sendXt=True):
        if locationId in self.locations:
            return False

        self.locations.append(locationId)
        self.session.add(LocationInventory(PenguinID=self.user.ID, LocationID=locationId))
        self.user.Coins -= locationCost

        if sendXt:
            self.sendXt("aloc", locationId, self.user.Coins)

    def addFurniture(self, furnitureId, furnitureCost=0, sendXt=True):
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

        if sendXt:
            self.sendXt("af", furnitureId, self.user.Coins)

    def addFlooring(self, floorId, floorCost=0, sendXt=True):
        if floorId in self.floors:
            return False

        self.floors.append(floorId)
        self.session.add(FloorInventory(PenguinID=self.user.ID, FloorID=floorId))
        self.user.Coins -= floorCost

        if sendXt:
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
        rankAwards = self.server.availableClothing["Ninja"]["CardJitsu"]
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
        if coinAmount > self.user.maxCoins:
            self.user.Coins = self.user.maxCoins
        else:
            self.user.Coins = coinAmount
        self.sendXt("zo", self.user.Coins, "", 0, 0, 0)

    def getPlayerString(self):
        playerArray = [
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
            self.user.Avatar,
            str(), # Unused value
            str() # Party information
        ]

        if self.walkingPuffle is not None:
            playerArray.extend([self.walkingPuffle.ID, self.walkingPuffle.Type,
                                self.walkingPuffle.Subtype if self.walkingPuffle.Subtype else str(),
                                self.walkingPuffle.Hat, 0])

        playerStringArray = map(str, playerArray)
        self.playerString = "|".join(playerStringArray)

        return self.playerString

    def connectionLost(self, reason):
        if hasattr(self, "room") and self.room is not None:
            self.room.remove(self)

        if self.user.ID in self.server.mascots:
            for playerId in self.server.players.keys():
                player = self.server.players[playerId]
                if self.user.ID in player.characterBuddies:
                    player.sendXt("crof", self.user.ID)
        else:
            for buddyId in self.buddies.keys():
                if buddyId in self.server.players and self.user.Moderator != 2:
                    self.server.players[buddyId].sendXt("bof", self.user.ID)

        loginUnix = time.mktime(self.login.Date.timetuple())
        minutesPlayed = int(time.time() - loginUnix) / 60
        self.user.MinutesPlayed += minutesPlayed
        self.user.OnlineStatus = None
        self.session.add(self.login)

        self.server.redis.srem("%s.players" % self.server.serverName, self.user.ID)
        self.server.redis.decr("%s.population" % self.server.serverName)

        super(Penguin, self).connectionLost(reason)
        # After the data has been committed; to ensure that the data was saved.
        map(self.session.expunge, self.igloos.values())
        map(self.session.expunge, self.puffles.values())

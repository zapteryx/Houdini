from datetime import datetime

from Houdini.Handlers import Handlers, XML
from Houdini.Data.Ban import Ban
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Penguin import PenguinRowProxy, Penguin, BuddyList, IgnoreList, IglooInventory, FurnitureInventory, Inventory
from Houdini.Data.Igloo import IglooRowProxy, Igloo
from Houdini.Data.Puffle import PuffleRowProxy, Puffle
from Houdini.Data.Deck import Deck
from Houdini.Crypto import Crypto

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import threads

from sqlalchemy.sql import select

@Handlers.Handle(XML.Login)
@Handlers.Throttle(-1)
@inlineCallbacks
def handleLogin(self, data):
    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))

    user = yield self.engine.first(Penguin.select(Penguin.c.Username == username))

    if user is None:
        returnValue(self.sendErrorAndDisconnect(100))

    if not user.LoginKey:
        returnValue(self.transport.loseConnection())

    loginHash = Crypto.encryptPassword(user.LoginKey + self.randomKey) + user.LoginKey

    if password != loginHash:
        self.logger.debug("{} failed to login.".format(username))

        returnValue(self.sendErrorAndDisconnect(101))

    if user.Permaban:
        returnValue(self.transport.loseConnection())

    currentDateTime = datetime.now()

    activeBan = yield self.engine.first(Ban.select((Ban.c.PenguinID == user.ID) & (Ban.c.Expires >= datetime.now())))

    if activeBan is not None:
        returnValue(self.transport.loseConnection())

    if user.ID in self.server.players:
        self.server.players[user.ID].transport.loseConnection()

    self.logger.info("{} logged in successfully".format(username))

    self.user = PenguinRowProxy(self.engine, user)

    ipAddr = self.transport.getPeer().host

    self.login = [datetime.now(), ipAddr]

    # Add them to the Redis set
    threads.deferToThread(self.server.redis.sadd, "{}.players".format(self.server.serverName), self.user.ID)
    threads.deferToThread(self.server.redis.incr, "{}.population".format(self.server.serverName))

    self.age = (currentDateTime - self.user.RegistrationDate).days

    stamps = yield self.engine.fetchall(select([Stamp.c.Stamp, Stamp.c.Recent]).where(Stamp.c.PenguinID == self.user.ID))
    self.stamps = [stampId for stampId, recent in stamps]
    self.recentStamps = [stampId for stampId, recent in stamps if recent]

    buddies = yield self.engine.fetchall(select([BuddyList.c.BuddyID, Penguin.c.Nickname])
                                         .select_from(BuddyList.join(Penguin, Penguin.c.ID == BuddyList.c.BuddyID))
                                         .where(BuddyList.c.PenguinID == self.user.ID))
    self.buddies = {buddyId: buddyNickname for buddyId, buddyNickname in buddies}

    ignore = yield self.engine.fetchall(select([IgnoreList.c.IgnoreID, Penguin.c.Nickname])
                                        .select_from(IgnoreList.join(Penguin, Penguin.c.ID == IgnoreList.c.IgnoreID))
                                        .where(IgnoreList.c.PenguinID == self.user.ID))
    self.ignore = {ignoreId: ignoreNickname for ignoreId, ignoreNickname in ignore}

    inventory = yield self.engine.fetchall(select([Inventory.c.ItemID]).where(Inventory.c.PenguinID == self.user.ID))
    self.inventory = [itemId for itemId, in inventory]

    furniture = yield self.engine.fetchall(select([FurnitureInventory.c.FurnitureID, FurnitureInventory.c.Quantity])
                                           .where(FurnitureInventory.c.PenguinID == self.user.ID))
    self.furniture = {furnitureId: quantity for furnitureId, quantity in furniture}

    deck = yield self.engine.fetchall(select([Deck.c.CardID, Deck.c.Quantity]).where(Deck.c.PenguinID == self.user.ID))
    self.deck = {cardId: quantity for cardId, quantity in deck}
    self.cards = [self.server.cards[cardId] for cardId, quantity in deck]

    igloos = yield self.engine.fetchall(select([IglooInventory.c.IglooID]).where(IglooInventory.c.PenguinID == self.user.ID))
    self.igloos = [iglooId for iglooId, in igloos]

    igloo = yield self.engine.first(Igloo.select(Igloo.c.PenguinID == self.user.ID))
    self.igloo = IglooRowProxy(self.engine, igloo) if igloo is not None else None

    puffles = yield self.engine.fetchall(Puffle.select(Puffle.c.PenguinID == self.user.ID))
    self.puffles = {puffle.ID: PuffleRowProxy(self.engine, puffle) for puffle in puffles}

    self.sendXt("l")

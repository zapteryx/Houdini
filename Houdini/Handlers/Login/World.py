from datetime import datetime

from Houdini.Handlers import Handlers, XML
from Houdini.Data.Login import Login
from Houdini.Data.Ban import Ban
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Penguin import Penguin, BuddyList, IgnoreList, IglooInventory, FurnitureInventory, Inventory
from Houdini.Data.Igloo import Igloo
from Houdini.Data.Puffle import Puffle
from Houdini.Data.Deck import Deck
from Houdini.Crypto import Crypto
from Houdini.Data import retryableTransaction

@Handlers.Handle(XML.Login)
@retryableTransaction()
def handleLogin(self, data):
    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))

    self.session.commit()
    user = self.session.query(Penguin).filter_by(Username=username).first()

    if user is None:
        return self.sendErrorAndDisconnect(100)

    if not user.LoginKey:
        return self.transport.loseConnection()

    loginHash = Crypto.encryptPassword(user.LoginKey + self.randomKey) + user.LoginKey

    if password != loginHash:
        self.logger.debug("{} failed to login.".format(username))

        return self.sendErrorAndDisconnect(101)

    if user.Permaban:
        return self.transport.loseConnection()

    currentDateTime = datetime.now()

    activeBan = self.session.query(Ban).filter(Ban.PenguinID == user.ID)\
        .filter(Ban.Expires >= currentDateTime).first()

    if activeBan is not None:
        return self.transport.loseConnection()

    if user.ID in self.server.players:
        self.server.players[user.ID].transport.loseConnection()

    self.logger.info("{} logged in successfully".format(username))

    self.session.add(user)
    self.user = user

    ipAddr = self.transport.getPeer().host

    self.login = Login(PenguinID=self.user.ID, Date=datetime.now(), IPAddress=ipAddr)

    # Add them to the Redis set
    self.server.redis.sadd("%s.players" % self.server.serverName, self.user.ID)
    self.server.redis.incr("%s.population" % self.server.serverName)

    self.sendXt("l")

    self.age = (currentDateTime - self.user.RegistrationDate).days

    stampQuery = self.session.query(Stamp.Stamp).filter_by(PenguinID=self.user.ID)
    self.stamps = [stampId for stampId, in stampQuery]
    self.recentStamps = [stampId for stampId, in stampQuery.filter_by(Recent=1)]

    self.buddies = {buddyId: buddyNickname for buddyId, buddyNickname in
                    self.session.query(BuddyList.BuddyID, Penguin.Nickname).
                    join(Penguin, Penguin.ID == BuddyList.BuddyID).
                    filter(BuddyList.PenguinID == self.user.ID)}

    self.ignore = {ignoreId: ignoreNickname for ignoreId, ignoreNickname in
                   self.session.query(IgnoreList.IgnoreID, Penguin.Nickname).
                   join(Penguin, Penguin.ID == IgnoreList.IgnoreID).
                   filter(IgnoreList.PenguinID == self.user.ID)}

    self.inventory = [itemId for itemId, in self.session.query(Inventory.ItemID).filter_by(PenguinID=self.user.ID)]

    self.furniture = {furnitureId: quantity for furnitureId, quantity in self.session.query(
        FurnitureInventory.FurnitureID, FurnitureInventory.Quantity).filter_by(PenguinID=self.user.ID)}

    self.deck = {cardId: quantity for cardId, quantity in self.session.query(
        Deck.CardID, Deck.Quantity).filter_by(PenguinID=self.user.ID)}

    self.cards = [self.server.cards[cardId] for cardId, quantity in self.deck.iteritems() for _ in xrange(quantity)]

    self.igloos = [iglooId for iglooId, in self.session.query(IglooInventory.IglooID).filter_by(PenguinID=self.user.ID)]
    self.igloo = self.session.query(Igloo).filter_by(PenguinID=self.user.ID).first()

    self.puffles = {puffle.ID: puffle for puffle in self.session.query(Puffle).filter_by(PenguinID=self.user.ID)}

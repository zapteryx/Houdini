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

@Handlers.Handle(XML.Login)
def handleLogin(self, data):
    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))


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


    if activeBan is not None:
        return self.transport.loseConnection()

    if user.ID in self.server.players:
        self.server.players[user.ID].transport.loseConnection()

    self.logger.info("{} logged in successfully".format(username))


    ipAddr = self.transport.getPeer().host


    # Add them to the Redis set
    self.server.redis.sadd("%s.players" % self.server.serverName, self.user.ID)
    self.server.redis.incr("%s.population" % self.server.serverName)

    self.sendXt("l")

    self.age = (currentDateTime - self.user.RegistrationDate).days







    self.cards = [self.server.cards[cardId] for cardId, quantity in self.deck.iteritems() for _ in xrange(quantity)]



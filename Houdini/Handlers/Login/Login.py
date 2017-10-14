from Houdini.Handlers import Handlers, XML
from Houdini.Data.Penguin import Penguin
from Houdini.Crypto import Crypto

import bcrypt

@Handlers.Handle(XML.VersionCheck)
def handleVersionCheck(self, data):
    if not data.Version == 153:
        self.sendXml({"body": {"action": "apiKO", "r": "0"}})
        self.transport.loseConnection()
    else:
        self.sendXml({"body": {"action": "apiOK", "r": "0"}})

@Handlers.Handle(XML.RandomKey)
def handleRandomKey(self, data):
    self.randomKey = "houdini"
    self.sendXml({"body": {"action": "rndK", "r": "-1"}, "k": self.randomKey})

# TODO Implement ban-checking and login attempt throttling
@Handlers.Handle(XML.Login)
def handleLogin(self, data):
    if self.randomKey is None:
        return self.transport.loseConnection()

    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))

    user = self.session.query(Penguin).filter_by(Username=username).first()

    if user is None:
        return self.sendErrorAndDisconnect(100)

    if not bcrypt.checkpw(password, user.Password):
        self.logger.debug("{} failed to login.".format(username))

        return self.sendErrorAndDisconnect(101)

    self.logger.info("{} logged in successfully".format(username))

    loginKey = Crypto.hash(self.randomKey[::-1])

    self.session.add(user)

    self.user = user
    self.user.LoginKey = loginKey

    self.getBuddyList()

    buddyWorlds = []

    serversConfig = self.server.config["Servers"]

    for serverName in serversConfig.keys():
        if serversConfig[serverName]["World"]:
            serverPlayers = self.server.redis.smembers("%s.players" % serverName)

            if not len(serverPlayers) > 0:
                self.logger.debug("Skipping buddy iteration for %s " % serverName)
                continue

            for buddyId in self.buddies.keys():
                if str(buddyId) in serverPlayers:
                    buddyWorlds.append(serversConfig[serverName]["Id"])
                    break

    self.sendXt("l", user.ID, loginKey, "|".join(buddyWorlds), '101,')

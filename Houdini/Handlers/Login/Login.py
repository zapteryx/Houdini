from Houdini.Handlers import Handlers, XML
from Houdini.Data.Penguin import Penguin, BuddyList
from Houdini.Data.Ban import Ban
from Houdini.Crypto import Crypto

import bcrypt, time

from datetime import datetime

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import threads

from sqlalchemy.sql import select

@Handlers.Handle(XML.Login)
@inlineCallbacks
def handleLogin(self, data):
    if self.randomKey is None:
        returnValue(self.transport.loseConnection())

    if not hasattr(self.server, "loginAttempts"):
        self.server.loginAttempts = {}

    loginTimestamp = time.time()
    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))

    user = yield self.engine.first(Penguin.select(Penguin.c.Username == username))

    if user is None:
        returnValue(self.sendErrorAndDisconnect(100))

    ipAddr = self.transport.getPeer().host

    passwordCorrect = yield threads.deferToThread(bcrypt.checkpw, password, user.Password)

    if not passwordCorrect:
        self.logger.info("{} failed to login.".format(username))

        if ipAddr in self.server.loginAttempts:
            lastFailedAttempt, failureCount = self.server.loginAttempts[ipAddr]

            failureCount = 1 if loginTimestamp - lastFailedAttempt >= self.server.server["LoginFailureTimer"] \
                else failureCount + 1

            self.server.loginAttempts[ipAddr] = [loginTimestamp, failureCount]

            if failureCount >= self.server.server["LoginFailureLimit"]:
                returnValue(self.sendErrorAndDisconnect(150))

        else:
            self.server.loginAttempts[ipAddr] = [loginTimestamp, 1]

        returnValue(self.sendErrorAndDisconnect(101))

    if ipAddr in self.server.loginAttempts:
        previousAttempt, failureCount = self.server.loginAttempts[ipAddr]

        maxAttemptsExceeded = failureCount >= self.server.server["LoginFailureLimit"]
        timerSurpassed = (loginTimestamp - previousAttempt) > self.server.server["LoginFailureTimer"]

        if maxAttemptsExceeded and not timerSurpassed:
            returnValue(self.sendErrorAndDisconnect(150))
        else:
            del self.server.loginAttempts[ipAddr]

    if not user.Active:
        returnValue(self.sendErrorAndDisconnect(900))

    if user.Permaban:
        returnValue(self.sendErrorAndDisconnect(603))

    activeBan = yield self.engine.first(Ban.select((Ban.c.PenguinID == user.ID) & (Ban.c.Expires >= datetime.now())))

    if activeBan is not None:
        hoursLeft = round((activeBan.Expires - datetime.now()).total_seconds() / 60 / 60)

        if hoursLeft == 0:
            returnValue(self.sendErrorAndDisconnect(602))

        else:
            self.sendXt("e", 601, hoursLeft)
            returnValue(self.transport.loseConnection())

    self.logger.info("{} logged in successfully".format(username))

    randomKey = Crypto.generateRandomKey()
    loginKey = Crypto.hash(randomKey[::-1])

    self.user = user
    self.engine.execute(Penguin.update(Penguin.c.ID == user.ID).values(LoginKey=loginKey))

    buddyWorlds = []
    worldPopulations = []

    serversConfig = self.server.config["Servers"]

    for serverName in serversConfig.keys():
        if serversConfig[serverName]["World"]:
            serverPopulation = yield threads.deferToThread(self.server.redis.get, "{}.population".format(serverName))

            if not serverPopulation is None:
                serverPopulation = int(serverPopulation) / (serversConfig[serverName]["Capacity"] / 6)
            else:
                serverPopulation = 0

            serverPlayers = yield threads.deferToThread(self.server.redis.smembers, "{}.players".format(serverName))

            worldPopulations.append("%s,%s" % (serversConfig[serverName]["Id"], serverPopulation))

            if not len(serverPlayers) > 0:
                self.logger.debug("Skipping buddy iteration for %s " % serverName)
                continue

            buddies = yield self.engine.fetchall(select([BuddyList.c.BuddyID]).where(BuddyList.c.PenguinID == self.user.ID))

            for buddyId, in buddies:
                if str(buddyId) in serverPlayers:
                    buddyWorlds.append(serversConfig[serverName]["Id"])
                    break

    self.sendXt("l", user.ID, loginKey, "|".join(buddyWorlds), "|".join(worldPopulations))
    self.transport.loseConnection()
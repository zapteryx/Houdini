import zope.interface, logging, os, re
from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers

from Houdini.Handlers.Play.Message import handleSendMessage
from Houdini.Handlers.Play.Pet import handleSendAdoptPuffle
from Houdini.Handlers.Play.Moderation import languageBan

from collections import Counter, OrderedDict

class OrderedCounter(Counter, OrderedDict):
    pass

class ChatFilter(object):
    zope.interface.implements(Plugin)

    author = "Spydar007"
    version = 0.1
    description = "Block bad words from chat and puffle names"

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        configFile = os.path.dirname(os.path.realpath(__file__)) + "/words"
        with open(configFile, "r") as fileHandle:
            self.words = fileHandle.read().split("\n")
            self.words = self.words[:-1]

        if self.server.server["World"]:
            Handlers.Message -= handleSendMessage
            Handlers.Message += self.handleSendMessage

            Handlers.AdoptPuffle -= handleSendAdoptPuffle
            Handlers.AdoptPuffle += self.handleSendAdoptPuffle

    @staticmethod
    def makeRegexBadWord(badWord):
        return "".join([char if count == 1 else char + "{" + str(count) + ",}"
                        for char, count in OrderedCounter(badWord).iteritems()])

    @staticmethod
    def removeSpecialChars(message):
        return "".join(e for e in message if e.isalnum())

    def isNaughty(self, string):
        cleanMessage = self.removeSpecialChars(string)
        self.logger.info("[ChatFilter] Checking '%s' against bad words list" % (string))
        for badWord in self.words:
            if re.search(badWord, cleanMessage):
                return True
        return False

    def handleSendMessage(self, player, data):
        if self.isNaughty(data.Message):
            self.logger.info("[ChatFilter] Disallowing %s from saying '%s'" % (player.user.Username, data.Message))
            return languageBan(self, player.user.ID)

        handleSendMessage(player, data)

    def handleSendAdoptPuffle(self, player, data):
        if self.isNaughty(data.Name):
            self.logger.info("[ChatFilter] %s tried to name a puffle '%s'" % (player.user.Username, data.Name))
            return player.sendError(441)
        handleSendAdoptPuffle(player, data)

    def ready(self):
        self.logger.info("ChatFilter plugin has been loaded!")
        self.logger.info("%d bad words loaded" % (len(self.words)))

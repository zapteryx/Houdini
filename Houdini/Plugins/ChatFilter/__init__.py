import zope.interface, logging, os, re
from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers

from Houdini.Handlers.Play.Message import handleSendMessage
from Houdini.Handlers.Play.Pet import handleCheckPuffleName, handleRainbowPuffleCheckName, handleSendAdoptPuffle
from Houdini.Handlers.Redemption.Code import handleRedeemSendPuffle
from Houdini.Handlers.Play.Moderation import languageBan, cheatBan

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

            Handlers.CheckPuffleName -= handleCheckPuffleName
            Handlers.CheckPuffleName += self.handleCheckPuffleName

            Handlers.RainbowPuffleCheckName -= handleRainbowPuffleCheckName
            Handlers.RainbowPuffleCheckName += self.handleRainbowPuffleCheckName

            Handlers.RedeemSendPuffle -= handleRedeemSendPuffle
            Handlers.RedeemSendPuffle += self.handleRedeemSendPuffle

    @staticmethod
    def makeRegexBadWord(badWord):
        return "".join([char if count == 1 else char + "{" + str(count) + ",}"
                        for char, count in OrderedCounter(badWord).iteritems()])

    @staticmethod
    def removeSpecialChars(message):
        return "".join(e for e in message if e.isalnum())

    def isPartNaughty(self, string):
        cleanMessage = self.removeSpecialChars(string)
        self.logger.info("[ChatFilter] Checking '%s' against bad words list" % (string))
        for badWord in self.words:
            if re.search(badWord, cleanMessage.lower()):
                return True
        return False

    def isNaughty(self, string):
        self.logger.info("[ChatFilter] Checking '%s' against bad words list" % (string))
        messageWords = string.lower().split(" ")
        for badWord in self.words:
            for word in messageWords:
                if badWord == word:
                    return True
        return False

    def handleSendMessage(self, player, data):
        if "Commands" in self.server.plugins:
            if data.Message.startswith(self.server.plugins["Commands"].commandPrefix):
                return
        if self.isNaughty(data.Message):
            self.logger.info("[ChatFilter] Warning %s for trying to say '%s'" % (player.user.Username, data.Message))
            return languageBan(self, player.user.ID)
        elif self.isPartNaughty(data.Message):
            self.logger.info("[ChatFilter] Disallowing %s from saying '%s'" % (player.user.Username, data.Message))
            return

        handleSendMessage(player, data)

    def handleSendAdoptPuffle(self, player, data):
        # The purpose of this function is to detect people sending the adoption packet without first checking the name
        # If this happens and it is bad, the player is hacking and gets banned
        if self.isNaughty(data.Name):
            self.logger.info("[ChatFilter] %s tried to adopt a puffle called '%s'" % (player.user.Username, data.Name))
            return cheatBan(player, player.user.ID, 72, "Attempting to force-name a puffle")

        handleSendAdoptPuffle(player, data)

    def handleCheckPuffleName(self, player, data):
        if self.isNaughty(data.Name):
            self.logger.info("[ChatFilter] %s tried to name a puffle '%s'" % (player.user.Username, data.Name))
            return player.sendXt("checkpufflename", data.Name, 0)

        handleCheckPuffleName(player, data)

    def handleRainbowPuffleCheckName(self, player, data):
        if self.isNaughty(data.Name):
            self.logger.info("[ChatFilter] %s tried to name a rainbow puffle '%s'" % (player.user.Username, data.Name))
            return player.sendError(441)

        handleRainbowPuffleCheckName(player, data)

    def handleRedeemSendPuffle(self, player, data):
        if self.isNaughty(data.Name):
            self.logger.info("[ChatFilter] %s tried to name a puffle '%s' (redemption)" % (player.user.Username, data.Name))
            return player.sendXt("rsp", data.Name, 0)

        handleRedeemSendPuffle(player, data)

    def ready(self):
        self.logger.info("ChatFilter plugin has been loaded!")
        self.logger.info("%d bad words loaded" % (len(self.words)))

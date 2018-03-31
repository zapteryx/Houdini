import os
import random

import zope.interface, logging
from twisted.internet import reactor

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers

class Bot(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "A bot plugin"

    id = 0
    name = None
    x, y = (0, 0)
    frame = 1
    membershipDays = 750

    # Set the attribute to None for random clothing
    clothing = None

    # If you set this to False, the bot will not automatically spawn in the room.
    # Instead, he will show up and disappear whenever he's needed.
    isStationary = True

    botString = None

    namesFile = "names.txt" # Path relative to this plugin
    namesFileUrl = "https://www.cs.cmu.edu/Groups/AI/areas/nlp/corpora/names/other/names.txt"
    namesList = None

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        self.namesFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.namesFile)

        if self.name is None: # Ooh~
            self.randomizeName()

        if self.clothing is None: # Lewd~! o//o
            self.randomizeClothing()

        self.updateString()

        Handlers.GetInventory += self.handleJoinRoom # For the initial room join
        Handlers.JoinRoom += self.handleJoinRoom
        Handlers.JoinPlayerIgloo += self.handleJoinRoom

    def addToRoom(self, player):
        player.sendXt("ap", self.botString)

    def removeFromRoom(self, player):
        player.sendXt("rp", self.id)

    # TODO: Don't join game rooms (?)
    def handleJoinRoom(self, player, data):
        if self.isStationary:
            self.addToRoom(player)

    def sendMessage(self, player, message):
        if not self.isStationary:
            reactor.callFromThread(self.addToRoom, player)

        reactor.callFromThread(player.sendXt, "sm", self.id, message)

        if not self.isStationary:
            # May need to proxy this call through callFromThread
            reactor.callLater(2, self.removeFromRoom, player)

    def ready(self):
        self.logger.info("Bot plugin has been loaded")

    def randomizeName(self):
        if not os.path.isfile(self.namesFile):
            self.downloadNames()

        if self.namesList is None:
            with open(self.namesFile, "r") as namesFile:
                self.namesList = namesFile.readlines()

        self.name = random.choice(self.namesList).strip()

    def randomizeClothing(self):
        allItems = self.server.items.schemaObjects.keys()

        # TODO: Exclude bait items probably (LAZY)
        headIds = [itemId for itemId in allItems if self.server.items.isItemHead(itemId)]
        faceIds = [itemId for itemId in allItems if self.server.items.isItemFace(itemId)]
        neckIds = [itemId for itemId in allItems if self.server.items.isItemNeck(itemId)]
        bodyIds = [itemId for itemId in allItems if self.server.items.isItemBody(itemId)]
        handIds = [itemId for itemId in allItems if self.server.items.isItemHand(itemId)]
        feetIds = [itemId for itemId in allItems if self.server.items.isItemFeet(itemId)]
        flagIds = [itemId for itemId in allItems if self.server.items.isItemPin(itemId)]
        photoIds = [itemId for itemId in allItems if self.server.items.isItemPhoto(itemId)]

        self.clothing = {
            "Color": random.randrange(1, 14),
            "Head": random.choice(headIds),
            "Face": random.choice(faceIds),
            "Neck": random.choice(neckIds),
            "Body": random.choice(bodyIds),
            "Hand": random.choice(handIds),
            "Feet": random.choice(feetIds),
            "Flag": random.choice(flagIds),
            "Photo": random.choice(photoIds)
        }

    def updateString(self):
        self.botString = ("{bot.id}|"
                          "{bot.name}|"
                          "1|"
                          "{Color}|"
                          "{Head}|"
                          "{Face}|"
                          "{Neck}|"
                          "{Body}|"
                          "{Hand}|"
                          "{Feet}|"
                          "{Flag}|"
                          "{Photo}|"
                          "{bot.x}|"
                          "{bot.y}|"
                          "{bot.frame}|"
                          "1|"
                          "{bot.membershipDays}".format(bot=self, **self.clothing))

    def downloadNames(self):
        import urllib2
        namesResponse = urllib2.urlopen(self.namesFileUrl)

        with open(self.namesFile, "w") as namesFile:
            namesFile.write(namesResponse.read())

        namesResponse.close()

        self.logger.info("[Bot] Names file has been downloaded.")
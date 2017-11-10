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
    name = "Harry"
    x, y = (0, 0)
    frame = 1
    membershipDays = 1440

    # Set the attribute to None for random clothing
    clothing = {
        "Color": 14,
        "Head": 413,
        "Face": 2063,
        "Neck": 3014,
        "Body": 288,
        "Hand": 5050,
        "Feet": 6069,
        "Flag": 578,
        "Photo": 973
    }

    # If you set this to False, the bot will not automatically spawn in the room.
    # Instead, he will show up and disappear whenever he's needed.
    isStationary = True

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        if self.clothing is None: # Lewd~! o//o
            import random

            allItems = self.server.items.keys()

            self.clothing = {
                "Color": random.randrange(1, 14),
                "Head": random.choice(allItems),
                "Face": random.choice(allItems),
                "Neck": random.choice(allItems),
                "Body": random.choice(allItems),
                "Hand": random.choice(allItems),
                "Feet": random.choice(allItems),
                "Flag": random.choice(allItems),
                "Photo": random.choice(allItems)
            }

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
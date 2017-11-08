import zope.interface, logging
from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Handlers.Play.Item import handleBuyInventory

# TODO: Implement thread-safety..? :fear:
class Commands(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "A commands plugin"

    commandPrefix = "!"

    # At some point we may make this its own module, but until then \o/
    botId = 0
    botName = "Harry"
    botString = None

    coinLimit = 1000000

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        self.commands = {
            "AC": {
                "Handler": self.handleCoinsCommand,
                "Arguments": [CommandArgument("Coins", int)]
            },

            "AI": {
                "Handler": self.handleItemCommand,
                "Arguments": [CommandArgument("ItemId", int)]
            },

            "PING": {
                "Handler": self.handlePingCommand,
                "Arguments": []
            }
        }

        Handlers.Message += self.handleMessage

        self.botString = "%d|%s|1|4|1099|0|172|225|0|352|0|904|0|0|1|1|1" % (self.botId, self.botName)

    # Maybe make a method for adding coins in the player class?
    def handleCoinsCommand(self, player, arguments):
        self.logger.debug("%s is trying to add %d coins" % (player.user.Username, arguments.Coins))

        player.user.Coins = max(min(self.coinLimit, player.user.Coins + arguments.Coins), 1)
        player.sendXt("zo", player.user.Coins, "", 0, 0, 0)

    def handleItemCommand(self, player, arguments):
        self.logger.debug("%s is trying to add an item (id: %d)" % (player.user.Username, arguments.ItemId))

        if not self.server.items.isBait(arguments.ItemId):
            handleBuyInventory(player, arguments)

    def handlePingCommand(self, player, arguments):
        self.logger.debug("Received ping command from %s" % player.user.Username)

        player.sendXt("ap", self.botString)
        player.sendXt("sm", self.botId, "Pong!")

        reactor.callLater(3, player.sendXt, "rp", self.botId)

    # Do not edit below this line.
    def processCommand(self, messageDetails):
        playerObject, commandMessage = messageDetails

        commandTokens = commandMessage.split(" ")
        commandString = commandTokens.pop(0).upper()

        if commandString not in self.commands:
            return  # Command doesn't exist!

        commandArguments = self.commands[commandString]["Arguments"]
        commandHandler = self.commands[commandString]["Handler"]

        if not commandArguments:
            return commandHandler(playerObject, None)

        commandData = CommandData()
        tokenIndex = 0
        for commandToken in commandTokens:
            commandArgument = commandArguments[tokenIndex]

            if commandArgument.argumentType is int:
                if not commandToken.isdigit():
                    raise Exception("%r had an invalid argument" % commandString)

                setattr(commandData, commandArguments[tokenIndex].arbitraryName, int(commandTokens[tokenIndex]))

            else:
                if not isinstance(commandArgument, basestring):
                    raise Exception("%r had an invalid argument" % commandString)

                setattr(commandData, commandArguments[tokenIndex].arbitraryName, str(commandTokens[tokenIndex]))

            tokenIndex += 1

        return commandHandler(playerObject, commandData)

    def handleCommandError(self, error):
        self.logger.error(error)

    def handleMessage(self, player, data):
        self.logger.info("[Commands] Received message from %s: '%s'" % (player.user.Username, data.Message))

        if data.Message.startswith(self.commandPrefix):
            commandMessage = data.Message[1:]

            deferToThread(self.processCommand, [player, commandMessage])\
                .addErrback(self.handleCommandError)

    def ready(self):
        self.logger.info("Commands plugin has been loaded!")

class CommandData:
    pass

class CommandArgument(object):

    def __init__(self, arbitraryName, argumentType):
        self.arbitraryName = arbitraryName
        self.argumentType = argumentType
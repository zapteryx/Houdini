import zope.interface, logging
from twisted.internet import reactor
from twisted.internet.threads import blockingCallFromThread, deferToThread

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Data.Penguin import Penguin
from Houdini.Handlers.Play.Item import handleBuyInventory
from Houdini.Handlers.Play.Moderation import moderatorBan, moderatorKick

class Commands(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "A commands plugin"

    commandPrefix = "!"

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
            },

            "JR": {
                "Handler": self.handleJoinRoomCommand,
                "Arguments": [CommandArgument("RoomId", int)]
            },

            "BAN": {
                "Handler": self.handleBanCommand,
                "Arguments": [CommandArgument("Username", str), CommandArgument("Duration", int),
                              VariableCommandArgument("Reason")]
            },

            "KICK": {
                "Handler": self.handleKickCommand,
                "Arguments": [CommandArgument("Username", str)]
            }
        }

        self.bot = self.server.plugins["Bot"]

        Handlers.Message += self.handleMessage

    @staticmethod
    def getPlayer(sessionObject, playerUsername, specificQuery=Penguin):
        player = sessionObject.query(specificQuery). \
            filter_by(Username=playerUsername).scalar()

        return player

    def handleKickCommand(self, player, arguments):
        if player.user.Moderator:
            playerId = blockingCallFromThread(reactor, self.getPlayer, player.session,
                                              arguments.Username, Penguin.ID)

            if playerId is not None and playerId in self.server.players:
                if not self.server.players[playerId].user.Moderator:
                    reactor.callFromThread(moderatorKick, player, playerId)

                    self.logger.info("%s has kicked %s" % (player.user.Username, arguments.Username))

    def handleBanCommand(self, player, arguments):
        if player.user.Moderator:
            banReason = " ".join(arguments.Reason)

            playerId = blockingCallFromThread(reactor, self.getPlayer, player.session,
                                              arguments.Username, Penguin.ID)

            if playerId is not None:
                reactor.callFromThread(moderatorBan, player, playerId,
                                       arguments.Duration, banReason)

                self.logger.info("%s has banned %s using the !BAN command." %
                                 (player.user.Username, arguments.Username))

    def handleJoinRoomCommand(self, player, arguments):
        if arguments.RoomId in self.server.rooms:
            player.x = 0
            player.y = 0
            player.frame = 1

            reactor.callFromThread(player.room.remove, player)
            reactor.callFromThread(self.server.rooms[arguments.RoomId].add, player)

    def handleCoinsCommand(self, player, arguments):
        self.logger.debug("%s is trying to add %d coins" % (player.user.Username, arguments.Coins))

        newAmount = max(min(self.coinLimit, player.user.Coins + arguments.Coins), 1)

        reactor.callFromThread(player.sendCoins, newAmount)

    def handleItemCommand(self, player, arguments):
        self.logger.debug("%s is trying to add an item (id: %d)" % (player.user.Username, arguments.ItemId))

        if not self.server.items.isBait(arguments.ItemId):
            reactor.callFromThread(handleBuyInventory, player, arguments)

    def handlePingCommand(self, player, arguments):
        self.logger.debug("Received ping command from %s" % player.user.Username)

        self.bot.sendMessage(player, "Pong!")

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

            if not isinstance(commandArgument, VariableCommandArgument):
                if commandArgument.argumentType is int:
                    if not commandToken.isdigit():
                        raise Exception("%r had an invalid argument" % commandString)

                    setattr(commandData, commandArgument.arbitraryName, int(commandTokens[tokenIndex]))

                else:
                    if commandArgument.argumentType is not str:
                        raise Exception("%r had an invalid argument" % commandString)

                    setattr(commandData, commandArgument.arbitraryName, str(commandTokens[tokenIndex]))
            else:
                setattr(commandData, commandArgument.arbitraryName, commandTokens[tokenIndex:])
                break

            tokenIndex += 1

            if tokenIndex > len(commandArguments) - 1:
                break

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

class VariableCommandArgument(object):

    def __init__(self, arbitraryName):
        self.arbitraryName = arbitraryName

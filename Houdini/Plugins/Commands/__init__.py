import zope.interface, logging
from twisted.internet import reactor
from twisted.internet.threads import blockingCallFromThread, deferToThread

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Data.Penguin import Penguin
from Houdini.Handlers.Play.Item import handleBuyInventory
from Houdini.Handlers.Play.Igloo import handleBuyFurniture, handleUpdateFloor, handleUpdateIglooType, handleBuyIglooLocation
from Houdini.Handlers.Play.Pet import handleAddPuffleCareItem
from Houdini.Handlers.Play.Moderation import moderatorBan, moderatorKick
from Houdini.Handlers.Play.Setting import handleSendUpdatePlayerColour, handleSendUpdatePlayerHead, handleSendUpdatePlayerFace, handleSendUpdatePlayerNeck, handleSendUpdatePlayerBody, handleSendUpdatePlayerHand, handleSendUpdatePlayerFeet, handleSendUpdatePlayerFlag, handleSendUpdatePlayerPhoto
from Houdini.Handlers.Play.PlayerTransformation import handlePlayerTransformation

commandCollection = {}

def Command(commandName, *commandArguments):
    def decoratorFunction(commandHandler):
        uppercaseCommand = commandName.upper()

        commandCollection[uppercaseCommand] = {
            "Handler": commandHandler,
            "Arguments": commandArguments
        }

        return commandHandler
    return decoratorFunction

class CommandArgument(object):

    def __init__(self, arbitraryName, argumentType):
        self.arbitraryName = arbitraryName
        self.argumentType = argumentType

class TokenizedArgument(CommandArgument):
    pass

class VariableCommandArgument(object):

    def __init__(self, arbitraryName):
        self.arbitraryName = arbitraryName

class Commands(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "A commands plugin"

    commandPrefix = "!"
    tokenizedDelimiter = " / "

    coinLimit = 1000000

    commands = {}

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        Handlers.Message += self.handleMessage

    @staticmethod
    def getPlayer(sessionObject, playerNickname, specificQuery=Penguin):
        player = sessionObject.query(specificQuery). \
            filter_by(Nickname=playerNickname).scalar()

        return player

    @Command("kick", VariableCommandArgument("Nickname"))
    def handleKickCommand(self, player, arguments):
        if player.user.Moderator != 0:
            playerId = blockingCallFromThread(reactor, self.getPlayer, player.session,
                                              arguments.Nickname, Penguin.ID)

            if playerId is not None and playerId in self.server.players:
                if self.server.players[playerId].user.Moderator == 0:
                    reactor.callFromThread(moderatorKick, player, playerId)

                    self.logger.info("%s has kicked %s" % (player.user.Nickname, arguments.Nickname))

    # Example: !BAN King Arthur / 24 / Not actually king.
    @Command("ban", TokenizedArgument("Nickname", str),
             TokenizedArgument("Duration", int),
             TokenizedArgument("Reason", str))
    def handleBanCommand(self, player, arguments):
        if player.user.Moderator != 0:
            self.logger.info("%s is attempting to ban %s." % (player.user.Nickname, arguments.Nickname))

            playerId = blockingCallFromThread(reactor, self.getPlayer, player.session,
                                              arguments.Nickname, Penguin.ID)

            if playerId is not None:
                reactor.callFromThread(moderatorBan, player, playerId,
                                       arguments.Duration, arguments.Reason)

                self.logger.info("%s has banned %s for %s hours using the !BAN command." %
                                 (player.user.Nickname, arguments.Nickname, arguments.Duration))

    @Command("jr", CommandArgument("RoomId", int))
    def handleJoinRoomCommand(self, player, arguments):
        if arguments.RoomId in self.server.rooms:
            if player.user.Moderator != 0:
                player.x = 0
                player.y = 0
                player.frame = 1

                reactor.callFromThread(player.joinRoom, arguments.RoomId)
            else:
                self.logger.debug("Denied %s from joining room %s - not Moderator" % (player.user.Nickname, arguments.RoomId))

    @Command("ac", CommandArgument("Coins", int))
    def handleCoinsCommand(self, player, arguments):
        self.logger.debug("%s is trying to add %d coins" % (player.user.Nickname, arguments.Coins))
        if player.user.Moderator != 0:
            newAmount = max(min(self.coinLimit, player.user.Coins + arguments.Coins), 1)

            reactor.callFromThread(player.sendCoins, newAmount)
        else:
            self.logger.debug("Denied %s from adding %d coins - not Moderator" % (player.user.Nickname, arguments.Coins))

    @Command("ai", CommandArgument("ItemId", int))
    def handleItemCommand(self, player, arguments):
        self.logger.debug("%s is trying to add an item (id: %d)" % (player.user.Nickname, arguments.ItemId))

        if arguments.ItemId not in self.server.items:
            self.logger.debug("Item (id: %d) does not exist" % (arguments.ItemId))
            return player.sendError(402)
        elif self.server.items.isBait(arguments.ItemId):
            self.logger.debug("Denied %s from adding item (id: %d) - item is bait" % (player.user.Nickname, arguments.ItemId))
            return player.sendError(402)
        else:
            reactor.callFromThread(handleBuyInventory, player, arguments)

    @Command("af", CommandArgument("FurnitureId", int))
    def handleFurnitureCommand(self, player, arguments):
        self.logger.debug("%s is trying to add furniture (id: %d)" % (player.user.Nickname, arguments.FurnitureId))

        if arguments.FurnitureId not in self.server.furniture:
            self.logger.debug("Furniture (id: %d) does not exist" % (arguments.FurnitureId))
            return player.sendError(402)
        elif self.server.furniture.isBait(arguments.FurnitureId):
            self.logger.debug("Denied %s from adding furniture (id: %d) - item is bait" % (player.user.Nickname, arguments.FurnitureId))
            return player.sendError(402)
        else:
            reactor.callFromThread(handleBuyFurniture, player, arguments)

    @Command("ag", CommandArgument("FloorId", int))
    def handleFloorCommand(self, player, arguments):
        self.logger.debug("%s is trying to add floor (id: %d)" % (player.user.Nickname, arguments.FloorId))

        if arguments.FloorId not in self.server.floors:
            self.logger.debug("Floor (id: %d) does not exist" % (arguments.FloorId))
            return player.sendError(402)
        else:
            reactor.callFromThread(handleUpdateFloor, player, arguments)

    @Command("au", CommandArgument("IglooId", int))
    def handleIglooCommand(self, player, arguments):
        self.logger.debug("%s is trying to add igloo (id: %d)" % (player.user.Nickname, arguments.IglooId))

        if arguments.IglooId not in self.server.igloos:
            self.logger.debug("Igloo (id: %d) does not exist" % (arguments.IglooId))
            return player.sendError(402)
        else:
            reactor.callFromThread(handleUpdateIglooType, player, arguments)

    @Command("aloc", CommandArgument("LocationId", int))
    def handleLocationCommand(self, player, arguments):
        self.logger.debug("%s is trying to add location (id: %d)" % (player.user.Nickname, arguments.LocationId))

        reactor.callFromThread(handleBuyIglooLocation, player, arguments)

    @Command("papi", CommandArgument("ItemId", int))
    def handlePuffleItemCommand(self, player, arguments):
        self.logger.debug("%s is trying to add a puffle item (id: %d)" % (player.user.Nickname, arguments.ItemId))

        reactor.callFromThread(handleAddPuffleCareItem, player, arguments)

    @Command("color", CommandArgument("ItemId", int))
    @Command("colour", CommandArgument("ItemId", int))
    def handleUpdateColorCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerColour, player, arguments)

    @Command("head", CommandArgument("ItemId", int))
    def handleUpdateHeadCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerHead, player, arguments)

    @Command("face", CommandArgument("ItemId", int))
    def handleUpdateFaceCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerFace, player, arguments)

    @Command("neck", CommandArgument("ItemId", int))
    def handleUpdateNeckCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerNeck, player, arguments)

    @Command("body", CommandArgument("ItemId", int))
    def handleUpdateBodyCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerBody, player, arguments)

    @Command("hand", CommandArgument("ItemId", int))
    def handleUpdateHandCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerHand, player, arguments)

    @Command("feet", CommandArgument("ItemId", int))
    def handleUpdateFeetCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerFeet, player, arguments)

    @Command("photo", CommandArgument("ItemId", int))
    @Command("background", CommandArgument("ItemId", int))
    @Command("bg", CommandArgument("ItemId", int))
    def handleUpdatePhotoCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerPhoto, player, arguments)

    @Command("flag", CommandArgument("ItemId", int))
    @Command("pin", CommandArgument("ItemId", int))
    def handleUpdateFlagCommand(self, player, arguments):
        reactor.callFromThread(handleSendUpdatePlayerFlag, player, arguments)

    @Command("transform", CommandArgument("TransformationId", int))
    @Command("spts", CommandArgument("TransformationId", int))
    @Command("up", CommandArgument("TransformationId", int))
    def handleTransformCommand(self, player, arguments):
        reactor.callFromThread(handlePlayerTransformation, player, arguments)

    # Do not edit below this line.
    def processCommand(self, messageDetails):
        playerObject, commandMessage = messageDetails

        commandTokens = commandMessage.split(" ")
        commandString = commandTokens.pop(0).upper()

        if commandString not in commandCollection:
            return  # Command doesn't exist!

        commandArguments = commandCollection[commandString]["Arguments"]
        commandHandler = commandCollection[commandString]["Handler"]

        if not commandArguments:
            return commandHandler(self, playerObject, None)

        # Better way to do this?
        if isinstance(commandArguments[0], TokenizedArgument):
            commandTokens = commandMessage.split(" ")[1:] # Remove the command itself
            commandTokens = " ".join(commandTokens).split(self.tokenizedDelimiter) # Rejoin and split by the delimiter

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

        return commandHandler(self, playerObject, commandData)

    def handleCommandError(self, error):
        self.logger.error(error)

    def handleMessage(self, player, data):
        self.logger.info("[Commands] Received message from %s: '%s'" % (player.user.Nickname, data.Message))

        if data.Message.startswith(self.commandPrefix):
            commandMessage = data.Message[1:]

            deferToThread(self.processCommand, [player, commandMessage])\
                .addErrback(self.handleCommandError)

    def ready(self):
        self.logger.info("Commands plugin has been loaded!")

class CommandData:
    pass



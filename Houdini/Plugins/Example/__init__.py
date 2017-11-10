import zope.interface, logging
from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Events import Events

class Example(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "A plugin to verify plugin system functionality and demonstrate implementation"

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        Handlers.Login += self.handleLogin

        # Only do this if the server is a world server
        if self.server.server["World"]:
            Handlers.JoinWorld += self.handleJoinWorld
            Handlers.JoinWorld -= self.handleJoinWorld

        Events.Connected += self.handleConnection
        Events.Disconnected += self.handleDisconnection

    def handleJoinWorld(self, player, data):
        self.logger.info("[Example] Holy smokes!")

    def handleLogin(self, player, data):
        self.logger.warn("[Example] %s is trying to login" % data.Username)

    @Events.Register("Connected")
    def handleConnected(player):
        print("[Example] Woohoo~!")

    @Events.Register("Disconnected")
    def handleDisconnected(player):
        print("[Example] Poo..~")

    def handleConnection(self, player):
        self.logger.info("[Example] New player connected, woohoo!")

    def handleDisconnection(self, player):
        self.logger.info("[Example] Aw, that sucks :-(")

    def ready(self):
        self.logger.info("Example plugin is ready!")
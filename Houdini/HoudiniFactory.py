import importlib
import logging
import os
import pkgutil
import sys
from logging.handlers import RotatingFileHandler

import redis
from sqlalchemy import create_engine
from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from watchdog.observers import Observer

from config import config
from Houdini import CacheRegion
import Houdini.Handlers as Handlers
import Houdini.Plugins as Plugins
from Houdini.Crumbs import retrieveItemCollection, retrieveRoomCollection, \
    retrieveFurnitureCollection, retrieveFloorCollection, retrieveIglooCollection, \
    retrievePinCollection, retrieveStampsCollection, retrieveCardCollection, \
    retrieveDanceCollection
from Houdini.Events import Events
from Houdini.Events.HandlerFileEvent import HandlerFileEventHandler
from Houdini.Events.PluginFileEvent import PluginFileEventHandler
from Houdini.Handlers.Play.Pet import decreaseStats
from Houdini.Handlers.Games import createTables, createWaddles
from Houdini.Handlers.Games.MatchMaking import MatchMaking
from Houdini.Handlers.Games.Dance import DanceFloor
from Houdini.Penguin import Penguin
from Houdini.Spheniscidae import Spheniscidae
from Houdini.Data import wrap_engine

"""Deep debug
from twisted.python import log
log.startLogging(sys.stdout)
"""

class HoudiniFactory(Factory):

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("Houdini")

        self.config = config

        self.serverName = kwargs["server"]
        self.server = self.config["Servers"][self.serverName]

        # Set up logging
        generalLogDirectory = os.path.dirname(self.server["Logging"]["General"])
        errorsLogDirectory = os.path.dirname(self.server["Logging"]["Errors"])

        if not os.path.exists(generalLogDirectory):
            os.mkdir(generalLogDirectory)

        if not os.path.exists(errorsLogDirectory):
            os.mkdir(errorsLogDirectory)

        universalHandler = RotatingFileHandler(self.server["Logging"]["General"],
                                               maxBytes=2097152, backupCount=3, encoding="utf-8")
        self.logger.addHandler(universalHandler)

        level = logging.getLevelName(self.server["Logging"]["Level"])
        self.logger.setLevel(level)

        errorHandler = logging.FileHandler(self.server["Logging"]["Errors"])
        errorHandler.setLevel(logging.ERROR)
        self.logger.addHandler(errorHandler)

        engineString = "mysql+{0}://{1}:{2}@{3}/{4}".format(
            self.config["Database"]["Driver"].lower(),
            self.config["Database"]["Username"],
            self.config["Database"]["Password"],
            self.config["Database"]["Address"],
            self.config["Database"]["Name"])

        self.databaseEngine = wrap_engine(reactor, create_engine(engineString, pool_recycle=3600, pool_pre_ping=True,
                                                                 pool_size=50, max_overflow=20))

        self.redis = redis.StrictRedis()
        self.redis.delete("%s.players" % self.serverName)
        self.redis.delete("%s.population" % self.serverName)

        self.players = {}

        self.logger.info("Houdini module initialized")

        self.handlers = {}

        if self.server["World"]:
            self.protocol = Penguin

            CacheRegion.configure(
                'dogpile.cache.memory',
                expiration_time=3600
            )

            self.spawnRooms = (100, 300, 400, 800, 809, 230, 130)

            self.rooms = retrieveRoomCollection()
            self.items = retrieveItemCollection()
            self.furniture = retrieveFurnitureCollection()
            self.igloos = retrieveIglooCollection()
            self.floors = retrieveFloorCollection()
            self.pins = retrievePinCollection()
            self.stampGroups, self.stamps = retrieveStampsCollection()
            self.cards = retrieveCardCollection()
            self.dance = retrieveDanceCollection()

            self.openIgloos = {}

            createTables(self.config["Tables"], self.rooms)
            createWaddles(self.config["Waddles"], self.rooms)
            self.danceFloor = DanceFloor(self.dance)

            self.puffleKiller = task.LoopingCall(decreaseStats, self)
            self.puffleKiller.start(1800)

            self.matchMaker = MatchMaking()

            self.loadHandlerModules(excludeLoad="Houdini.Handlers.Login.Login")
            self.logger.info("Running world server")
        else:
            self.protocol = Spheniscidae
            self.loadHandlerModules("Houdini.Handlers.Login.Login")
            self.logger.info("Running login server")

        self.plugins = {}
        self.loadPlugins()

    def loadPlugins(self):
        for pluginPackage in self.getPackageModules(Plugins):
            self.loadPlugin(pluginPackage)

    def loadPlugin(self, plugin):
        pluginModule, pluginClass = plugin

        if not pluginClass in self.server["Plugins"]:
            return

        pluginObject = getattr(pluginModule, pluginClass)(self)

        if Plugins.Plugin.providedBy(pluginObject):
            self.plugins[pluginClass] = pluginObject

            reactor.callInThread(pluginObject.ready)

        else:
            self.logger.warn("{0} plugin object doesn't provide the plugin interface".format(pluginClass))

    def loadHandlerModules(self, strictLoad=None, excludeLoad=None):
        for handlerModule in self.getPackageModules(Handlers):
            if not (strictLoad and handlerModule not in strictLoad or excludeLoad and handlerModule in excludeLoad):
                if handlerModule not in sys.modules.keys():
                    importlib.import_module(handlerModule)

        self.logger.info("Handler modules loaded")

    def getPackageModules(self, package):
        packageModules = []

        for importer, moduleName, isPackage in pkgutil.iter_modules(package.__path__):
            fullModuleName = "{0}.{1}".format(package.__name__, moduleName)

            if isPackage:
                subpackageObject = importlib.import_module(fullModuleName, package=package.__path__)
                subpackageObjectDirectory = dir(subpackageObject)

                if "Plugin" in subpackageObjectDirectory:
                    packageModules.append((subpackageObject, moduleName))

                    continue

                subPackageModules = self.getPackageModules(subpackageObject)

                packageModules = packageModules + subPackageModules
            else:
                packageModules.append(fullModuleName)

        return packageModules

    def buildProtocol(self, addr):
        player = self.protocol(self.databaseEngine, self)

        Events.Fire("Connected", player)

        return player

    def configureObservers(self, *observerSettings):
        for observerPath, observerClass in observerSettings:
            eventObserver = Observer()
            eventObserver.schedule(observerClass(self), observerPath, recursive=True)
            eventObserver.start()

    def start(self):
        self.logger.info("Starting server..")

        port = self.server["Port"]

        handlersPath = "./Houdini{}Handlers".format(os.path.sep)
        pluginsPath = "./Houdini{}Plugins".format(os.path.sep)

        self.configureObservers([handlersPath, HandlerFileEventHandler],
                                [pluginsPath, PluginFileEventHandler])

        self.logger.info("Listening on port {0}".format(port))

        reactor.listenTCP(port, self)
        reactor.run()

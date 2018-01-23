import importlib
import json
import logging
import os
import pkgutil
import sys
from logging.handlers import RotatingFileHandler

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from watchdog.observers import Observer

import Houdini.Handlers as Handlers
import Houdini.Plugins as Plugins
from Houdini.Crumbs import retrieveItemCollection, retrieveRoomCollection, \
    retrieveFurnitureCollection, retrieveFloorCollection, retrieveIglooCollection, \
    retrievePinCollection, retrieveStampsCollection
from Houdini.Events import Events
from Houdini.Events.HandlerFileEvent import HandlerFileEventHandler
from Houdini.Events.PluginFileEvent import PluginFileEventHandler
from Houdini.Handlers.Play.Pet import decreaseStats
from Houdini.Handlers.Games.Table import Table
from Houdini.Handlers.Games.FindFour import FindFour
from Houdini.Handlers.Games.Mancala import Mancala
from Houdini.Handlers.Games.Waddle import Waddle, SledRace
from Houdini.Penguin import Penguin
from Houdini.Spheniscidae import Spheniscidae

"""Deep debug
from twisted.python import log
log.startLogging(sys.stdout)
"""

class HoudiniFactory(Factory):

    def __init__(self, *kw, **kwargs):
        self.logger = logging.getLogger("Houdini")

        configFile = kw[0]
        with open(configFile, "r") as fileHandle:
            self.config = json.load(fileHandle)

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

        errorHandler = logging.FileHandler(self.server["Logging"]["Errors"])
        errorHandler.setLevel(logging.ERROR)
        self.logger.addHandler(errorHandler)

        engineString = "mysql://{0}:{1}@{2}/{3}".format(self.config["Database"]["Username"],
                                                        self.config["Database"]["Password"],
                                                        self.config["Database"]["Address"],
                                                        self.config["Database"]["Name"])

        self.databaseEngine = create_engine(engineString, pool_recycle=3600)
        self.createSession = sessionmaker(bind=self.databaseEngine)
        self.session = self.createSession()

        self.redis = redis.StrictRedis()
        self.redis.flushdb()

        self.players = {}

        self.logger.info("Houdini module initialized")

        self.handlers = {}

        if self.server["World"]:
            self.protocol = Penguin

            self.spawnRooms = (100, 300, 400, 800, 809, 230, 130)

            self.rooms = retrieveRoomCollection()
            self.items = retrieveItemCollection()
            self.furniture = retrieveFurnitureCollection()
            self.igloos = retrieveIglooCollection()
            self.floors = retrieveFloorCollection()
            self.pins = retrievePinCollection()
            self.stampGroups, self.stamps = retrieveStampsCollection()

            self.openIgloos = {}

            self.createTables()
            self.createWaddles()

            self.puffleKiller = task.LoopingCall(decreaseStats, self)
            self.puffleKiller.start(1800)

            self.loadHandlerModules(excludeLoad="Houdini.Handlers.Login.Login")
            self.logger.info("Running world server")
        else:
            self.protocol = Spheniscidae
            self.loadHandlerModules("Houdini.Handlers.Login.Login")
            self.logger.info("Running login server")

        self.plugins = {}
        self.loadPlugins()

    def createTables(self):
        tablesConfig = self.config["Tables"]
        tableTypes = [("Four", FindFour), ("Mancala", Mancala), ("Treasure", FindFour)]

        for tableType in tableTypes:
            typeKey, typeClass = tableType
            tableRooms = tablesConfig[typeKey]

            for room in tableRooms:
                roomObject = self.rooms[room["RoomId"]]
                tableIds = room["Tables"]

                for tableId in tableIds:
                    tableObject = Table(tableId, typeClass, roomObject)
                    roomObject.tables[tableId] = tableObject

    def createWaddles(self):
        waddlesConfig = self.config["Waddles"]
        waddleTypes = [("Sled", SledRace)]

        for waddleType in waddleTypes:
            typeKey, typeClass = waddleType
            waddleRooms = waddlesConfig[typeKey]

            for room in waddleRooms:
                roomObject = self.rooms[room["RoomId"]]
                waddles = room["Waddles"]

                for waddle in waddles:
                    waddleObject = Waddle(waddle["Id"], waddle["Seats"],
                                          typeClass, roomObject)
                    roomObject.waddles[waddle["Id"]] = waddleObject

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
        player = self.protocol(self.session, self)

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

import logging
import json
import os
import pkgutil
import sys
import importlib

from watchdog.observers import Observer
from logging.handlers import RotatingFileHandler

import redis

from twisted.internet.protocol import Factory
from twisted.internet import reactor, task

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import Houdini.Handlers as Handlers
from Houdini.HandlerFileEventHandler import HandlerFileEventHandler
from Houdini.Spheniscidae import Spheniscidae
from Houdini.Penguin import Penguin
from Houdini.Crumbs import retrieveItemCollection, retrieveRoomCollection,\
    retrieveFurnitureCollection, retrieveFloorCollection, retrieveIglooCollection
from Houdini.Handlers.Play.Pet import decreaseStats

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

        self.redis = redis.StrictRedis()

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

            self.loadPins()
            self.loadGameStamps()

            self.openIgloos = {}

            self.puffleKiller = task.LoopingCall(decreaseStats, self)
            self.puffleKiller.start(1800)

            self.loadHandlerModules()
            self.logger.info("Running world server")
        else:
            self.protocol = Spheniscidae
            self.loadHandlerModules("Houdini.Handlers.Login.Login")
            self.logger.info("Running login server")

    def loadHandlerModules(self, strictLoad=()):
        for handlerModule in self.getPackageModules(Handlers):
            if not strictLoad or strictLoad and handlerModule in strictLoad:

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

    def loadPins(self):
        if not hasattr(self, "pins"):
            self.pins = {}

        def parsePinCrumbs():
            with open("crumbs/pins.json", "r") as fileHandle:
                pins = json.load(fileHandle)

                for pin in pins:
                    pinId = int(pin["paper_item_id"])
                    self.pins[pinId] = pin

            self.logger.info("{0} pins loaded".format(len(self.pins)))

        if not os.path.exists("crumbs/pins.json"):
            self.logger.warn("Unable to read pins.json")
        else:
            parsePinCrumbs()

    def loadGameStamps(self):
        if not hasattr(self, "stamps"):
            self.stamps = {}

        def parseStampCrumbs():
            with open("crumbs/stamps.json", "r") as stampFileHandle:
                stampCollection = json.load(stampFileHandle)

                with open("crumbs/rooms.json", "r") as roomFileHandle:
                    roomsCollection = json.load(roomFileHandle).values()

                    for stampCategory in stampCollection:
                        if stampCategory["parent_group_id"] == 8:
                            for roomObject in roomsCollection:
                                if stampCategory["display"].replace("Games : ", "") == roomObject["display_name"]:
                                    roomId = roomObject["room_id"]
                                    self.stamps[roomId] = []
                                    break

                            for stampObject in stampCategory["stamps"]:
                                self.stamps[roomId].append(stampObject["stamp_id"])

            # print(json.dumps(self.stamps))

        if not os.path.exists("crumbs/stamps.json"):
            self.logger.warn("Unable to load crumbs/stamps.json")
        else:
            parseStampCrumbs()

    def buildProtocol(self, addr):
        session = self.createSession()

        player = self.protocol(session, self)

        return player

    def start(self):
        self.logger.info("Starting server..")

        port = self.server["Port"]

        handlerEventObserver = Observer()
        handlerEventObserver.schedule(HandlerFileEventHandler(), "./Houdini/Handlers", recursive=True)
        handlerEventObserver.start()

        self.logger.info("Listening on port {0}".format(port))

        reactor.listenTCP(port, self)
        reactor.run()

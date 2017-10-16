import logging
import json
import os
import pkgutil
import sys
import importlib

from types import FunctionType
from watchdog.observers import Observer
from logging.handlers import RotatingFileHandler

import redis

from twisted.web.client import getPage
from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import Handlers
from HandlerFileEventHandler import HandlerFileEventHandler
from Spheniscidae import Spheniscidae
from Penguin import Penguin
from Room import Room

""" For debugging
from twisted.python import log
log.startLogging(sys.stdout)
"""

class Houdini(Factory):

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

            self.loadRooms()
            self.spawnRooms = (100, 300, 400, 800, 809, 230, 130)

            self.loadItems()
            self.loadIgloos()
            self.loadFloors()
            self.loadPins()

            self.openIgloos = {}

            self.loadHandlerModules()
            self.logger.info("Running world server")
        else:
            self.protocol = Spheniscidae
            self.loadHandlerModules("Houdini.Handlers.Login.Login")
            self.logger.info("Running login server")

    def loadHandlerModules(self, strictLoad=()):
        handlerMethods = []

        def populateHandlerMethods(moduleObject):
            moduleMethods = [getattr(moduleObject, attribute) for attribute in dir(moduleObject)
                             if isinstance(getattr(moduleObject, attribute), FunctionType)]

            for moduleMethod in moduleMethods:
                handlerMethods.append(moduleMethod)

        for handlerModule in self.getPackageModules(Handlers):
            if not strictLoad or strictLoad and handlerModule in strictLoad:

                if handlerModule not in sys.modules.keys():
                    moduleObject = importlib.import_module(handlerModule)

                    populateHandlerMethods(moduleObject)

                else:
                    self.logger.info("Reloading module {0}".format(handlerModule))

                    handlersCopy = self.handlers.copy()

                    for handlerId, handlerMethod in handlersCopy.iteritems():
                        # self.events.off(handlerId, handlerMethod)
                        self.handlers.pop(handlerId, None)

                    moduleObject = sys.modules[handlerModule]
                    moduleObject = reload(moduleObject)

                    populateHandlerMethods(moduleObject)

        for handlerId, listenerList in Handlers.Handlers.XMLHandlers.iteritems():
            for handlerListener in listenerList:
                handlerMethod = handlerListener.function

                if handlerMethod in handlerMethods:
                    self.handlers[handlerId] = handlerMethod

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

    def downloadCrumbs(self, url):
        deferredDownload = defer.Deferred()

        def handleRequestComplete(resultData):
            decodedResult = resultData.decode('utf-8')
            crumbsFilename = os.path.basename(url.decode('utf-8'))

            if not os.path.exists("crumbs"):
                os.makedirs("crumbs")

            crumbsFile = "crumbs/{0}".format(crumbsFilename)

            with open(crumbsFile, "w") as fileHandler:
                fileHandler.write(decodedResult)

            deferredDownload.callback(None)

        getPage(url).addCallback(handleRequestComplete)

        return deferredDownload

    def loadIgloos(self):
        if not hasattr(self, "igloos"):
            self.igloos = {}

        def praseIglooCrumbs(downloadResult=None):
            with open("crumbs/igloos.json", "r") as fileHandle:
                igloos = json.load(fileHandle)

                for iglooId, iglooDetails in igloos.items():
                    iglooId = int(iglooId)
                    self.igloos[iglooId] = int(iglooDetails["cost"])

            self.logger.info("{0} igloos loaded".format(len(self.igloos)))

        if not os.path.exists("crumbs/igloos.json"):
            self.downloadCrumbs("http://media.localhost/en/web_service/game_configs/igloos.json") \
                .addCallback(praseIglooCrumbs)

        else:
            praseIglooCrumbs()

    def loadFloors(self):
        if not hasattr(self, "floors"):
            self.floors = {}

        def parseFloorCrumbs(downloadResult=None):
            with open("crumbs/igloo_floors.json", "r") as fileHandle:
                floors = json.load(fileHandle)

                for floor in floors:
                    floorId = int(floor["igloo_floor_id"])
                    self.floors[floorId] = int(floor["cost"])

            self.logger.info("{0} igloo floors loaded".format(len(self.floors)))

        if not os.path.exists("crumbs/igloo_floors.json"):
            self.downloadCrumbs("http://media.localhost/en/web_service/game_configs/igloo_floors.json") \
                .addCallback(parseFloorCrumbs)

        else:
            parseFloorCrumbs()

    def loadItems(self):
        if not hasattr(self, "items"):
            self.items = {}

        def parseItemCrumbs(downloadResult=None):
            with open("crumbs/paper_items.json", "r") as fileHandle:
                items = json.load(fileHandle)

                for item in items:
                    itemId = int(item["paper_item_id"])
                    self.items[itemId] = item

            self.logger.info("{0} items loaded".format(len(self.items)))

        if not os.path.exists("crumbs/paper_items.json"):
            self.downloadCrumbs("http://media.localhost/en/web_service/game_configs/paper_items.json") \
                .addCallback(parseItemCrumbs)

        else:
            parseItemCrumbs()

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


    def loadRooms(self):
        if not hasattr(self, "rooms"):
            self.rooms = {}

        def parseRoomCrumbs(downloadResult=None):
            with open("crumbs/rooms.json", "r") as fileHandle:
                rooms = json.load(fileHandle).values()

                internalId = 0

                for room in rooms:
                    externalId = room["room_id"]
                    internalId += 1

                    if not externalId in self.rooms:
                        self.rooms[externalId] = Room(externalId, internalId)

            self.logger.info("{0} rooms loaded".format(len(self.rooms)))

        if not os.path.exists("crumbs/rooms.json"):
            self.downloadCrumbs("http://media.localhost/en/web_service/game_configs/rooms.json") \
                .addCallback(parseRoomCrumbs)

        else:
            parseRoomCrumbs()

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

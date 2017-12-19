import zope.interface, logging, json, os, time, subprocess, re, itertools
from sys import platform
from glob import glob
from twisted.internet import threads

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Handlers.Play.Item import handleBuyInventory
from Houdini.Handlers.Play.Igloo import handleBuyFurniture, handleUpdateIglooType, handleUpdateFloor

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MediaFileEventHandler(FileSystemEventHandler):

    def __init__(self, patchedItems):
        self.pluginObject = patchedItems
        self.lastScan = time.time()

    def on_any_event(self, event):
        if time.time() > self.lastScan + 300:
            d = threads.deferToThread(self.pluginObject.scanPatchables)
            d.addCallback(self.pluginObject.updatePatchables)

            self.lastScan = time.time()

class PatchedItems(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "Plugin automatically scans flash media and whitelists items."

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        configFile = os.path.dirname(os.path.realpath(__file__)) + "/patched.conf"
        with open(configFile, "r") as fileHandle:
            self.config = json.load(fileHandle)

        self.mediaPath = self.config["Media"]
        self.subdirectories = self.config["Subdirectories"]

        self.whitelist = self.config["Patched"]["Whitelist"]
        self.blacklist = self.config["Patched"]["Blacklist"]
        self.exceptions = self.config["Patched"]["Exceptions"]
        self.additionalWhitelist = bool(self.whitelist["Clothing"] or self.whitelist["Furniture"] or \
                                   self.whitelist["Igloos"] or self.whitelist["Flooring"])
        self.blacklistEnabled = bool(self.blacklist["Clothing"] or self.blacklist["Furniture"] or \
                                   self.blacklist["Igloos"] or self.blacklist["Flooring"])
        self.whitelistExceptions = bool(self.exceptions["Clothing"] or self.exceptions["Furniture"] or \
                                   self.exceptions["Igloos"] or self.exceptions["Flooring"])

        if self.blacklistEnabled:
            self.logger.warn("Blacklist patching is enabled! Any whitelisting you have "
                             "configured will be ignored!")
            self.patchedClothing = self.blacklist["Clothing"]
            self.patchedFurniture = self.blacklist["Furniture"]
            self.patchedIgloos = self.blacklist["Igloos"]
            self.patchedFlooring = self.blacklist["Flooring"]

        self.patchableClothing = []
        self.patchableFurniture = []
        self.patchableIgloos = []
        self.patchableFlooring = []

        self.flasmExecutable = self.getFlasmBin()

        self.mediaEventObserver = Observer()

        Handlers.BuyInventory -= handleBuyInventory
        Handlers.BuyInventory += self.handleBuyInventory

        Handlers.BuyFurniture -= handleBuyFurniture
        Handlers.BuyFurniture += self.handleBuyFurniture

        Handlers.UpdateIglooType -= handleUpdateIglooType
        Handlers.UpdateIglooType += self.handleUpdateIglooType

        Handlers.UpdateFloor -= handleUpdateFloor
        Handlers.UpdateFloor += self.handleUpdateFloor

    def handleBuyInventory(self, player, data):
        if not self.blacklistEnabled and data.ItemId not in self.patchableClothing:
            return player.sendError(402)
        elif self.blacklistEnabled and data.ItemId in self.patchedClothing:
            return player.sendError(402)

        handleBuyInventory(player, data)

    def handleBuyFurniture(self, player, data):
        if not self.blacklistEnabled and data.FurnitureId not in self.patchableFurniture:
            return player.sendError(402)
        elif self.blacklistEnabled and data.FurnitureId in self.patchableFurniture:
            return player.sendError(402)

        handleBuyFurniture(player, data)

    def handleUpdateIglooType(self, player, data):
        if not self.blacklistEnabled and data.IglooId not in self.patchableIgloos:
            return player.sendError(402)
        elif self.blacklistEnabled and data.IglooId in self.patchedIgloos:
            return player.sendError(402)

        handleUpdateIglooType(player, data)

    def handleUpdateFloor(self, player, data):
        if not self.blacklistEnabled and data.FloorId not in self.patchableFlooring:
            return player.sendError(402)
        elif self.blacklistEnabled and data.FloorId in self.patchableFlooring:
            return player.sendError(402)

        handleUpdateFloor(player, data)

    def scanPatchables(self):
        self.logger.info("Scanning for patchables...")

        items, furniture, igloos, flooring = [], [], [], []
        for subdirectory in self.subdirectories:
            directoryScan = [y for x in os.walk(self.mediaPath + subdirectory) for y in glob(os.path.join(x[0], '*.swf'))]
            for path in directoryScan:
                workingDir = os.path.dirname(os.path.realpath(__file__))
                disFlash = subprocess.check_output([workingDir + self.flasmExecutable, '-d', path])

                items += self.disassembledItemIds(disFlash)
                furniture += self.disassembledItemIds(disFlash, "buyFurniture")
                igloos += self.disassembledItemIds(disFlash, "buyIglooUpgrade")
                flooring += self.disassembledItemIds(disFlash, "buyIglooFloor")

        return list(set(items)), list(set(furniture)), list(set(igloos)), list(set(flooring))

    def updatePatchables(self, patchables):
        self.patchableClothing, self.patchableFurniture, \
        self.patchableIgloos, self.patchableFlooring = patchables

        if self.additionalWhitelist:
            self.patchableClothing += self.whitelist["Clothing"]
            self.patchableFurniture += self.whitelist["Furniture"]
            self.patchableIgloos += self.whitelist["Igloos"]
            self.patchableFlooring += self.whitelist["Flooring"]

        if self.whitelistExceptions:
            self.patchableClothing = [x for x in self.patchableClothing if x not in self.exceptions["Clothing"]]
            self.patchableFurniture = [x for x in self.patchableFurniture if x not in self.exceptions["Furniture"]]
            self.patchableIgloos = [x for x in self.patchableIgloos if x not in self.exceptions["Igloos"]]
            self.patchableFlooring = [x for x in self.patchableFlooring if x not in self.exceptions["Flooring"]]

        self.logger.info("Found {0} patchable clothing items".format(len(self.patchableClothing)))
        self.logger.info("Found {0} patchable furniture items".format(len(self.patchableFurniture)))
        self.logger.info("Found {0} patchable igloo items".format(len(self.patchableIgloos)))
        self.logger.info("Found {0} patchable flooring items".format(len(self.patchableFlooring)))

    def ready(self):
        if not self.blacklistEnabled:
            d = threads.deferToThread(self.scanPatchables)
            d.addCallback(self.updatePatchables)

            self.mediaEventObserver.schedule(MediaFileEventHandler(self), self.mediaPath, recursive=True)
            self.mediaEventObserver.start()

        self.logger.info("PatchedItems plugin has been loaded!")

    @staticmethod
    def disassembledItemIds(disassembledFlash, scriptFuncName = "buyInventory"):
        idsFound, search = [], []
        for i in range(1, 5):
            results = re.finditer(r'push \d+(.+\n){' + str(i) + '}.+push \'%s\'' % scriptFuncName, disassembledFlash)
            if results: search.append(results)
        search = itertools.chain.from_iterable(search)
        for results in search:
            resultId = re.search(r'push (\d+)', results.group())
            resultId = int(resultId.group(1))
            idsFound.append(resultId)
        if idsFound:
            results = re.finditer(r'push \'itemArray\'(.*\n){2}.+push.+?,(( \d+,)+)', disassembledFlash)
            for item in results:
                resultIds = re.findall(r'(\d+)(, ?)', item.group(2))
                idsFound += [int(x[0]) for x in resultIds]
        return idsFound

    @staticmethod
    def getFlasmBin():
        if platform == "linux" or platform == "linux2":
            return '/flasm/linux/flasm'
        elif platform == "darwin":
            return '/flasm/mac/flasm'
        elif platform == "win32":
            return '/flasm/win/flasm.exe'
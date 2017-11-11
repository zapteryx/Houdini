import logging
import sys
import importlib
from os.path import sep as pathSeparator
from watchdog.events import FileSystemEventHandler
import twisted.python.rebuild as rebuild

from Houdini.Handlers import Handlers

class HandlerFileEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.logger = logging.getLogger("Houdini")

    def createDeepCopy(self, collection):
        newCollection = {}

        for handlerId, listenerArray in collection.items():
            newCollection[handlerId] = list(listenerArray)

        return newCollection

    def removeHandlersByModule(self, handlerModulePath):
        def removeHandlers(handlerItems):
            for handlerId, handlerListeners in handlerItems:
                for handlerListener in handlerListeners:
                    if handlerListener.functionFile == handlerModulePath:
                        handlerListeners.remove(handlerListener)
                        self.logger.debug("Removed %s", handlerId)

        handlerItems = Handlers.XTHandlers.items()
        xtHandlerCollection = self.createDeepCopy(Handlers.XTHandlers)
        removeHandlers(handlerItems)

        handlerItems = Handlers.XMLHandlers.items()
        xmlHandlerCollection = self.createDeepCopy(Handlers.XMLHandlers)
        removeHandlers(handlerItems)

        return xtHandlerCollection, xmlHandlerCollection

    def evaluateHandlerFileEvent(self, handlerFileEvent):
        # Ignore all directory events
        if handlerFileEvent.is_directory:
            return False

        handlerModulePath = handlerFileEvent.src_path[2:]

        # Ignore non-Python files
        if handlerModulePath[-3:] != ".py":
            return False

        handlerModule = handlerModulePath.replace(pathSeparator, ".")[:-3]

        return handlerModulePath, handlerModule

    def on_created(self, event):
        handlerModuleDetails = self.evaluateHandlerFileEvent(event)

        if not handlerModuleDetails:
            return

        handlerModulePath, handlerModule = handlerModuleDetails

        if "__init__.py" in handlerModulePath:
            return

        self.logger.debug("New handler module detected %s", handlerModule)

        try:
            importlib.import_module(handlerModule)

        except Exception as importError:
            self.logger.error("%s detected in %s, not importing.", importError.__class__.__name__, handlerModule)

    def on_deleted(self, event):
        handlerModuleDetails = self.evaluateHandlerFileEvent(event)

        if not handlerModuleDetails:
            return

        handlerModulePath, handlerModule = handlerModuleDetails

        if handlerModule not in sys.modules:
            return

        self.logger.debug("Deleting listeners registered by %s..", handlerModule)

        self.removeHandlersByModule(handlerModulePath)

    def on_modified(self, event):
        handlerModuleDetails = self.evaluateHandlerFileEvent(event)

        if not handlerModuleDetails:
            return

        handlerModulePath, handlerModule = handlerModuleDetails

        if handlerModule not in sys.modules:
            return False

        self.logger.info("Reloading %s", handlerModule)

        xtHandlersCollection, xmlHandlersCollection = self.removeHandlersByModule(handlerModulePath)

        handlerModuleObject = sys.modules[handlerModule]

        try:
            rebuild.rebuild(handlerModuleObject)

            self.logger.info("Successfully reloaded %s!", handlerModule)

        except Exception as rebuildError:
            self.logger.error("%s detected in %s, not reloading.", rebuildError.__class__.__name__, handlerModule)
            self.logger.info("Restoring handler references...")

            Handlers.XTHandlers = xtHandlersCollection
            Handlers.XMLHandlers = xmlHandlersCollection

            self.logger.info("Handler references restored. Phew!")
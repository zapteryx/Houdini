import logging
import sys
import importlib
from watchdog.events import FileSystemEventHandler
import twisted.python.rebuild as rebuild

from Houdini.Handlers import Handlers
from Houdini.Events import evaluateHandlerFileEvent, removeHandlersByModule

class HandlerFileEventHandler(FileSystemEventHandler):

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")
        self.server = server

    def on_created(self, event):
        handlerModuleDetails = evaluateHandlerFileEvent(event)

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
        handlerModuleDetails = evaluateHandlerFileEvent(event)

        if not handlerModuleDetails:
            return

        handlerModulePath, handlerModule = handlerModuleDetails

        if handlerModule not in sys.modules:
            return

        self.logger.debug("Deleting listeners registered by %s..", handlerModule)

        removeHandlersByModule(handlerModulePath)

    def on_modified(self, event):
        handlerModuleDetails = evaluateHandlerFileEvent(event)

        if not handlerModuleDetails:
            return

        handlerModulePath, handlerModule = handlerModuleDetails

        if handlerModule not in sys.modules:
            return False

        self.logger.info("Reloading %s", handlerModule)

        xtHandlersCollection, xmlHandlersCollection = removeHandlersByModule(handlerModulePath)

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
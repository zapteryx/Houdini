import logging
import sys
import copy
from watchdog.events import FileSystemEventHandler
import twisted.python.rebuild as rebuild

from Handlers import Handlers

class HandlerFileEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.logger = logging.getLogger("Houdini")

    def on_modified(self, event):
        # Ignore all directory events
        if event.is_directory:
            return

        handlerModulePath = event.src_path[2:]
        handlerModule = handlerModulePath.replace("/", ".")[:-3]

        if handlerModule not in sys.modules:
            return

        self.logger.debug("Reloading %s", handlerModule)

        if "Houdini.Handlers.Play" in handlerModule:
            handlerItems = Handlers.XTHandlers.items()
            handlerCollection = copy.deepcopy(Handlers.XTHandlers)

        else:
            handlerItems = Handlers.XMLHandlers.items()
            handlerCollection = copy.deepcopy(Handlers.XMLHandlers)

        for handlerId, handlerListeners in handlerItems:
            for handlerListener in handlerListeners:
                # Look through the list of listeners to determine which need to be removed
                # self.logger.debug("Comparing %s to %s", handlerListener.functionFile, handlerModulePath)

                if handlerListener.functionFile == handlerModulePath:
                    self.logger.debug("Removing a %s listener", handlerId)
                    handlerListeners.remove(handlerListener)

        handlerModuleObject = sys.modules[handlerModule]

        try:
            rebuild.rebuild(handlerModuleObject)

        except (IndentationError, SyntaxError) as rebuildError:
            self.logger.error("%s detected in %s, not reloading.", rebuildError.__class__.__name__, handlerModule)
            self.logger.info("Restoring handler references...")

            if "Houdini.Handlers.Play" in handlerModule:
                Handlers.XTHandlers = handlerCollection
            else:
                Handlers.XMLHandlers = handlerCollection

            self.logger.info("Handler references restored. Phew!")
        except:
            self.logger.error("Unable to reload %s due to an unknown reason!", handlerModule)
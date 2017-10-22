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

        self.logger.debug("%s triggered this event", event.src_path)

        handlerModulePath = event.src_path[2:]
        handlerModule = handlerModulePath.replace("/", ".")[:-3]

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

        try:
            handlerModuleObject = sys.modules[handlerModule]
            rebuild.rebuild(handlerModuleObject)

        except KeyError:
            self.logger.warn("Attempted to reload a module outside of the server's scope. This is currently normal.")
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
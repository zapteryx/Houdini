import logging
import sys
from watchdog.events import FileSystemEventHandler
import twisted.python.rebuild as rebuild

from Handlers import Handlers

class HandlerFileEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.logger = logging.getLogger("Houdini")

    def on_modified(self, event):
        self.logger.debug("%s triggered this event", event.src_path)

        handlerModulePath = event.src_path[2:]
        handlerModule = handlerModulePath.replace("/", ".").replace(".py", "")

        self.logger.debug("Reloading %s~", handlerModule)

        handlerItems = Handlers.XTHandlers.items() \
            if "Houdini.Handlers.Play" in handlerModule else Handlers.XMLHandlers.items()

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
        except (IndentationError, SyntaxError):
            self.logger.error("Syntax/indentation error detected in %s, not reloading.", handlerModule)
        except:
            self.logger.error("Unable to reload %s due to an unknown reason!", handlerModule)
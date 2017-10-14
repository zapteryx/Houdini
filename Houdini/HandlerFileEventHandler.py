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
                self.logger.debug("Comparing %s to %s", handlerListener.functionFile, handlerModulePath)

                if handlerListener.functionFile == handlerModulePath:
                    self.logger.debug("Removing a %s listener", handlerId)
                    handlerListeners.remove(handlerListener)

        handlerModuleObject = sys.modules[handlerModule]
        rebuild.rebuild(handlerModuleObject)
import logging
import sys
import importlib
from os.path import sep as pathSeparator

from watchdog.events import FileSystemEventHandler
import twisted.python.rebuild as rebuild

from Houdini.Handlers import Handlers
from Houdini.Events import Events, evaluateHandlerFileEvent, evaluatePluginFileEvent, \
                                    removeHandlersByModule, removeEventsByInstance, createDeepCopy

class PluginFileEventHandler(FileSystemEventHandler):

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")
        self.server = server

    def on_created(self, event):
        pluginModuleDetails = evaluateHandlerFileEvent(event)

        if not pluginModuleDetails:
            return

        pluginModulePath, pluginModule = pluginModuleDetails

        self.logger.debug("New handler module detected %s", pluginModule)

        try:
            pluginModuleObject = importlib.import_module(pluginModule)
            pluginClass = pluginModuleObject.__name__.split(".")[2]

            pluginObject = getattr(pluginModuleObject, pluginClass)(self.server)
            self.server.plugins[pluginClass] = pluginObject

            self.logger.info("New plugin '%s' has been loaded." % pluginClass)

        except Exception as importError:
            self.logger.error("%s detected in %s, not importing.", importError.__class__.__name__, pluginModule)

    def on_deleted(self, event):
        pluginModulePath = event.src_path[2:]

        pluginModule = pluginModulePath.replace(pathSeparator, ".")

        if pluginModule not in sys.modules:
            return

        self.logger.debug("Deleting listeners registered by %s..", pluginModule)

        pluginModuleObject = sys.modules[pluginModule]
        pluginClass = pluginModuleObject.__name__.split(".")[2]

        del self.server.plugins[pluginClass]

        removeEventsByInstance(pluginModuleObject)

        pluginModulePath += "{}__init__.py".format(pathSeparator)
        removeHandlersByModule(pluginModulePath)

    def on_modified(self, event):
        pluginModuleDetails = evaluatePluginFileEvent(event)

        if not pluginModuleDetails:
            return

        pluginModulePath, pluginModule = pluginModuleDetails

        if pluginModule not in sys.modules:
            return

        self.logger.info("Reloading %s", pluginModule)

        xtHandlersCollection, xmlHandlersCollection = removeHandlersByModule(pluginModulePath)
        eventHandlersCollection = createDeepCopy(Events.EventHandlers)

        pluginModuleObject = sys.modules[pluginModule]
        pluginClass = pluginModuleObject.__name__.split(".")[2]

        try:
            removeEventsByInstance(pluginModuleObject)

            newPluginModule = rebuild.rebuild(pluginModuleObject)
            newPluginObject = getattr(newPluginModule, pluginClass)(self.server)
            self.server.plugins[pluginClass] = newPluginObject

            self.logger.info("Successfully reloaded %s!", pluginModule)

        except LookupError as lookupError:
            self.logger.warn("Did not reload plugin '%s': %s." % (pluginClass, lookupError.message))

        except Exception as rebuildError:
            self.logger.error("%s detected in %s, not reloading.", rebuildError.__class__.__name__, pluginModule)
            self.logger.info("Restoring handler references...")

            Handlers.XTHandlers = xtHandlersCollection
            Handlers.XMLHandlers = xmlHandlersCollection
            Events.EventHandlers = eventHandlersCollection

            self.logger.info("Handler references restored. Phew!")
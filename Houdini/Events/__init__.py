class HandlerEvent(object):

    def __init__(self, eventName):
        self.eventName = eventName

    def __add__(self, eventHandler):
        if self.eventName not in Events.EventHandlers:
            Events.EventHandlers[self.eventName] = []

        Events.EventHandlers[self.eventName].append(eventHandler)

        return self

    def __sub__(self, eventHandler):
        if self.eventName in Events.EventHandlers:
            if eventHandler in Events.EventHandlers[self.eventName]:
                Events.EventHandlers[self.eventName].remove(eventHandler)

        return self

class EventsMeta(type):

    def __getattr__(self, eventName):
        return HandlerEvent(eventName)

class Events:
    __metaclass__ = EventsMeta
    EventHandlers = {}

    @staticmethod
    def Register(eventName, eventHandler):
        if eventName not in Events.EventHandlers:
            Events.EventHandlers[eventName] = []

        Events.EventHandlers[eventName].append(eventHandler)

        return eventHandler

    @staticmethod
    def Unregister(eventName, eventHandler):
        if eventName in Events.EventHandlers:
            if eventHandler in Events.EventHandlers[eventName]:
                Events.EventHandlers[eventName].remove(eventHandler)

    @staticmethod
    def Fire(eventName, *data):
        if eventName in Events.EventHandlers:
            for eventHandler in Events.EventHandlers[eventName]:
                eventHandler(*data)

# File event handler utility functions
import logging
logger = logging.getLogger("Houdini")

import inspect
from os.path import sep as pathSeparator
from Houdini.Handlers import Handlers

def createDeepCopy(collection):
    newCollection = {}

    for handlerId, listenerArray in collection.items():
        newCollection[handlerId] = list(listenerArray)

    return newCollection

def evaluateHandlerFileEvent(handlerFileEvent):
    # Ignore all directory events
    if handlerFileEvent.is_directory:
        return False

    handlerModulePath = handlerFileEvent.src_path[2:]

    # Ignore non-Python files
    if handlerModulePath[-3:] != ".py":
        return False

    handlerModule = handlerModulePath.replace(pathSeparator, ".")[:-3]

    return handlerModulePath, handlerModule

def evaluatePluginFileEvent(pluginFileEvent):
    # Ignore all directory events
    if pluginFileEvent.is_directory:
        return False

    handlerModulePath = pluginFileEvent.src_path[2:]

    # Ignore non-Python files
    if handlerModulePath[-3:] != ".py":
        return False

    # Remove file extension and replace path separator with dots. Then make like a banana.. and split.
    handlerModuleTokens = handlerModulePath.replace(pathSeparator, ".")[:-3].split(".")

    if handlerModuleTokens.pop() == "__init__":
        return handlerModulePath, ".".join(handlerModuleTokens)

    return False

def removeHandlersByModule(handlerModulePath):
    def removeHandlers(handlerItems):
        for handlerId, handlerListeners in handlerItems:
            for handlerListener in handlerListeners:
                if handlerListener.functionFile == handlerModulePath:
                    handlerListeners.remove(handlerListener)
                    logger.debug("Removed %s", handlerId)

    handlerItems = Handlers.XTHandlers.items()
    xtHandlerCollection = createDeepCopy(Handlers.XTHandlers)
    removeHandlers(handlerItems)

    handlerItems = Handlers.XMLHandlers.items()
    xmlHandlerCollection = createDeepCopy(Handlers.XMLHandlers)
    removeHandlers(handlerItems)

    return xtHandlerCollection, xmlHandlerCollection

def removeEventsByInstance(objectInstance):
    objectFilePath = inspect.getfile(objectInstance)

    # Workarounds for problems with the inspect module
    if objectFilePath is not None and "__init__.py" not in objectFilePath:
        objectFilePath += "{}__init__.py".format(pathSeparator)
    else:
        objectFilePath = objectInstance.__file__

        if objectFilePath[-4:] == ".pyc":
            objectFilePath = objectFilePath[:-4] + ".py"

    for eventName in Events.EventHandlers:
        for eventHandler in Events.EventHandlers[eventName]:
            if inspect.getfile(eventHandler) == objectFilePath:
                Events.EventHandlers[eventName].remove(eventHandler)
                logger.debug("Removed %s event" % eventName)
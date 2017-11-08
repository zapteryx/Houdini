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
    def Register(eventName):
        def eventWrapperFunction(eventHandler):
            if eventName not in Events.EventHandlers:
                Events.EventHandlers[eventName] = []

            Events.EventHandlers[eventName].append(eventHandler)

            return eventHandler

        return eventWrapperFunction

    @staticmethod
    def Unregister(eventName, eventHandler):
        if eventName in Events.EventHandlers:
            if eventHandler in Events.EventHandlers[eventName]:
                Events.EventHandlers[eventName].remove(eventHandler)

    @staticmethod
    def Fire(eventName, *data):
        for eventHandler in Events.EventHandlers[eventName]:
            eventHandler(*data)

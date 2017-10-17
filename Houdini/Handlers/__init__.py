import inspect
import os

class Data:
    pass

class XMLData:
    def __init__(self, arbitraryName, dataType, lambdaExtractor):
        self.name = arbitraryName
        self.type = dataType
        self.extractor = lambdaExtractor

class XML:
    RandomKey = {
        "Handler": "rndK",
        "Data": []
    }

    VersionCheck = {
        "Handler": "verChk",
        "Data": [XMLData("Version", int, lambda xmlData: xmlData[0].get("v"))]
    }

    Login = {
        "Handler": "login",
        "Data": [XMLData("Username", str, lambda xmlData: xmlData[0][0].text),
                 XMLData("Password", str, lambda xmlData: xmlData[0][1].text)]
    }

def getRelativeFunctionPath(functionObj):
    absFunctionFile = inspect.getfile(functionObj)
    relFunctionFile = os.path.relpath(absFunctionFile)

    return relFunctionFile

class XMLListener(object):

    def __init__(self, xmlHandler, xmlFunction):
        self.handler = xmlHandler
        self.function = xmlFunction

        self.functionFile = getRelativeFunctionPath(self.function)

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)

class XTListener(object):

    def __init__(self, xtHandler, xtFunction):
        self.handler = xtHandler
        self.function = xtFunction

        self.functionFile = getRelativeFunctionPath(self.function)

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)

class XTData:
    def __init__(self, arbitraryName, dataType):
        self.name = arbitraryName
        self.type = dataType

class VariableXTData:
    def __init__(self, arbitraryName):
        self.name = arbitraryName

class XT:
    JoinWorld = {
        "Handler": "j#js",
        "Data": [XTData("ID", int), XTData("LoginKey", str), XTData("Language", str)]
    }

    JoinRoom = {
        "Handler": "j#jr",
        "Data": [XTData("RoomId", int), XTData("X", int), XTData("Y", int)]
    }

    GetInventory = {
        "Handler": "i#gi",
        "Data": []
    }

    Heartbeat = {
        "Handler": "u#h",
        "Data": []
    }

    BuyInventory = {
        "Handler": "i#ai",
        "Data": [XTData("ItemId", int)]
    }

    GetPlayerPins = {
        "Handler": "i#qpp",
        "Data": [XTData("PlayerId", int)]
    }

    GetPlayerAwards = {
        "Handler": "i#qpa",
        "Data": [XTData("PlayerId", int)]
    }

    UpdateColor = {
        "Handler": "s#upc",
        "Data": [XTData("ItemId", int)]
    }

    UpdateHead = {
        "Handler": "s#uph",
        "Data": [XTData("ItemId", int)]
    }

    UpdateFace = {
        "Handler": "s#upf",
        "Data": [XTData("ItemId", int)]
    }

    UpdateNeck = {
        "Handler": "s#upn",
        "Data": [XTData("ItemId", int)]
    }

    UpdateBody = {
        "Handler": "s#upb",
        "Data": [XTData("ItemId", int)]
    }

    UpdateHand = {
        "Handler": "s#upa",
        "Data": [XTData("ItemId", int)]
    }

    UpdateFeet = {
        "Handler": "s#upe",
        "Data": [XTData("ItemId", int)]
    }

    UpdateFlag = {
        "Handler": "s#upl",
        "Data": [XTData("ItemId", int)]
    }

    UpdatePhoto = {
        "Handler": "s#upp",
        "Data": [XTData("ItemId", int)]
    }

    Message = {
        "Handler": "m#sm",
        "Data": [XTData("Id", int), XTData("Message", str)]
    }

    ThrowBall = {
        "Handler": "u#sb",
        "Data": [XTData("X", int), XTData("Y", int)]
    }

    PlayerMove = {
        "Handler": "u#sp",
        "Data": [XTData("X", int), XTData("Y", int)]
    }

    PlayerAction = {
        "Handler": "u#sa",
        "Data": [XTData("Id", int)]
    }

    SendEmote = {
        "Handler": "u#se",
        "Data": [XTData("Id", int)]
    }

    PlayerFrame = {
        "Handler": "u#sf",
        "Data": [XTData("Id", int)]
    }

    SendJoke = {
        "Handler": "u#sj",
        "Data": [XTData("Id", int)]
    }

    SendSafe = {
        "Handler": "u#ss",
        "Data": [XTData("Id", int)]
    }

    SendTourGuide = {
        "Handler": "u#sg",
        "Data": [XTData("Id", int)]
    }

    GetLatestRevision = {
        "Handler": "u#glr",
        "Data": []
    }

    GetBuddyList = {
        "Handler": "b#gb",
        "Data": []
    }

    BuddyRequest = {
        "Handler": "b#br",
        "Data": [XTData("Id", int)]
    }

    BuddyAccept = {
        "Handler": "b#ba",
        "Data": [XTData("Id", int)]
    }

    RemoveBuddy = {
        "Handler": "b#rb",
        "Data": [XTData("Id", int)]
    }

    FindBuddy = {
        "Handler": "b#bf",
        "Data": [XTData("Id", int)]
    }

    GetPlayer = {
        "Handler": "u#gp",
        "Data": [XTData("Id", int)]
    }

    GetIglooDetails = {
        "Handler": "g#gm",
        "Data": [XTData("Id", int)]
    }

    JoinPlayerIgloo = {
        "Handler": "j#jp",
        "Data": [XTData("Id", int)]
    }

    GetOwnedIgloos = {
        "Handler": "g#go",
        "Data": []
    }

    UpdateIglooMusic = {
        "Handler": "g#um",
        "Data": [XTData("MusicId", int)]
    }

    GetFurnitureList = {
        "Handler": "g#gf",
        "Data": []
    }

    UpdateFloor = {
        "Handler": "g#ag",
        "Data": [XTData("FloorId", int)]
    }

    UpdateIglooType = {
        "Handler": "g#au",
        "Data": [XTData("IglooId", int)]
    }

    BuyFurniture = {
        "Handler": "g#af",
        "Data": [XTData("FurnitureId", int)]
    }

    SaveIglooFurniture = {
        "Handler": "g#ur",
        "Data": [VariableXTData("FurnitureList")]
    }

    SendActivateIgloo = {
        "Handler": "g#ao",
        "Data": [XTData("TypeId", int)]
    }

    LoadPlayerIglooList = {
        "Handler": "g#gr",
        "Data": []
    }

    UnlockIgloo = {
        "Handler": "g#or",
        "Data": []
    }

    LockIgloo = {
        "Handler": "g#cr",
        "Data": []
    }

    StartMailEngine = {
        "Handler": "l#mst",
        "Data": []
    }

    GetMail = {
        "Handler": "l#mg",
        "Data": []
    }

    SendMail = {
        "Handler": "l#ms",
        "Data": [XTData("RecipientId", int), XTData("PostcardId", int)]
    }

    MailChecked = {
        "Handler": "l#mc",
        "Data": []
    }

    DeleteMail = {
        "Handler": "l#md",
        "Data": [XTData("PostcardId", int)]
    }

    DeleteMailFromUser = {
        "Handler": "l#mdp",
        "Data": [XTData("SenderId", int)]
    }

    StampAdd = {
        "Handler": "st#sse",
        "Data": [XTData("StampId", int)]
    }

    GetBookCover = {
        "Handler": "st#gsbcd",
        "Data": [XTData("PlayerId", int)]
    }

    GetStamps = {
        "Handler": "st#gps",
        "Data": [XTData("PlayerId", int)]
    }

    GetRecentStamps = {
        "Handler": "st#gmres",
        "Data": []
    }

    UpdateBookCover = {
        "Handler": "st#ssbcd",
        "Data": [VariableXTData("StampCover")]
    }

    GetPlayerPuffles = {
        "Handler": "p#pg",
        "Data": [XTData("Id", int)]
    }

    AdoptPuffle = {
        "Handler": "p#pn",
        "Data": [XTData("TypeId", int), XTData("Name", str)]
    }

    GetMyPlayerPuffles = {
        "Handler": "p#pgu",
        "Data": []
    }

# TODO implement PossibleXTData/PossibleXMLData?
class Handlers:
    XTHandlers = {}
    XMLHandlers = {}

    @staticmethod
    def HandleXML(clientObject, actionId, bodyTag):
        xmlListeners = Handlers.XMLHandlers[actionId]
        xmlHandlerDataStructure = xmlListeners[0].handler["Data"]
        xmlData = Data()

        if xmlHandlerDataStructure:
            for xmlHandlerDataObject in xmlHandlerDataStructure:
                xmlHandlerDataObjectValue = xmlHandlerDataObject.extractor(bodyTag)

                if xmlHandlerDataObject.type is int:
                    if not xmlHandlerDataObjectValue.isdigit():
                        return False

                    setattr(xmlData, xmlHandlerDataObject.name, int(xmlHandlerDataObjectValue))

                elif xmlHandlerDataObject.type is str:
                    if not isinstance(xmlHandlerDataObjectValue, basestring):
                        return False

                    setattr(xmlData, xmlHandlerDataObject.name, str(xmlHandlerDataObjectValue))

        for xmlListener in xmlListeners:
            xmlListener(clientObject, xmlData)

    @staticmethod
    def HandleXT(clientObject, packetId, packetData):
        xtListeners = Handlers.XTHandlers[packetId]
        xtHandlerDataStructure = xtListeners[0].handler["Data"]
        xtData = Data()

        # TODO: Catch IndexError exceptions
        if xtHandlerDataStructure:
            dataIndex = 4

            if not isinstance(xtHandlerDataStructure[0], VariableXTData):
                for xtHandlerDataObject in xtHandlerDataStructure:
                    xtHandlerDataObjectValue = packetData[dataIndex]

                    if xtHandlerDataObject.type is int:
                        if not xtHandlerDataObjectValue.isdigit():
                            return False

                        setattr(xtData, xtHandlerDataObject.name, int(xtHandlerDataObjectValue))

                    elif xtHandlerDataObject.type is str:
                        if not isinstance(xtHandlerDataObjectValue, basestring):
                            return False

                        setattr(xtData, xtHandlerDataObject.name, str(xtHandlerDataObjectValue))

                    dataIndex +=1
            else:
                xtHandlerDataObject = xtHandlerDataStructure[0]
                setattr(xtData, xtHandlerDataObject.name, packetData[dataIndex:])

        try:
            for xtListener in xtListeners:
                xtListener(clientObject, xtData)

        except Exception:
            clientObject.logger.exception("Uh oh! Caught potentially fatal error.")

    @staticmethod
    def Handle(handler):
        def handlerFunction(function):
            if not hasattr(function, "__call__"):
                return function

            handlerId = handler["Handler"]
            XT = True if "#" in handlerId else False

            if XT:
                if handlerId not in Handlers.XTHandlers:
                    Handlers.XTHandlers[handlerId] = []

                Handlers.XTHandlers[handlerId].append(XTListener(handler, function))

            else:
                if handlerId not in Handlers.XMLHandlers:
                    Handlers.XMLHandlers[handlerId] = []

                Handlers.XMLHandlers[handlerId].append(XMLListener(handler, function))

            return function

        return handlerFunction

    @staticmethod
    def HandlerExists(handlerId, handlerType):
        if handlerType == "XML":
            return handlerId in Handlers.XMLHandlers

        return handlerId in Handlers.XTHandlers

    @staticmethod
    def Remove(handler, handlerFunction):
        handlerId = handler["Handler"]
        if '#' not in handlerId: # TODO properly determine XT packets
            for xmlListener in Handlers.XMLHandlers[handlerId]:
                if xmlListener.function == handlerFunction:
                    Handlers.XMLHandlers[handlerId].remove(xmlListener)

                    break
        else:
            pass # TODO XT removal

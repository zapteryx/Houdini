import inspect, os, time

from Houdini.Data import retryableTransaction

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

    RefreshRoom = {
        "Handler": "j#grs",
        "Data": []
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

    SendLineMessage = {
        "Handler": "u#sl",
        "Data": [XTData("Id", int)]
    }

    SendMascotMessage = {
        "Handler": "u#sma",
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

    GetIgnoreList = {
        "Handler": "n#gn",
        "Data": []
    }

    AddIgnore = {
        "Handler": "n#an",
        "Data": [XTData("PlayerId", int)]
    }

    RemoveIgnore = {
        "Handler": "n#rn",
        "Data": [XTData("PlayerId", int)]
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
        "Data": [XTData("PlayerId", int)]
    }

    AdoptPuffle = {
        "Handler": "p#pn",
        "Data": [XTData("TypeId", int), XTData("Name", str)]
    }

    GetMyPlayerPuffles = {
        "Handler": "p#pgu",
        "Data": []
    }

    MovePuffle = {
        "Handler": "p#pm",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    WalkPuffle = {
        "Handler": "p#pw",
        "Data": [XTData("PuffleId", int), XTData("Walking", int)]
    }

    PlayPuffle = {
        "Handler": "p#pp",
        "Data": [XTData("PuffleId", int)]
    }

    PuffleFrame = {
        "Handler": "p#ps",
        "Data": [XTData("PuffleId", int), XTData("FrameId", int)]
    }

    GetAgentStatus = {
        "Handler": "f#epfga",
        "Data": []
    }

    SetAgentStatus = {
        "Handler": "f#epfsa",
        "Data": []
    }

    GetFieldOpStatus = {
        "Handler": "f#epfgf",
        "Data": []
    }

    SetFieldOpStatus = {
        "Handler": "f#epfsf",
        "Data": [XTData("FieldOpStatus", int)]
    }

    GetEpfPoints = {
        "Handler": "f#epfgr",
        "Data": []
    }

    BuyEpfItem = {
        "Handler": "f#epfai",
        "Data": [XTData("ItemId", int)]
    }

    GetCoinReward = {
        "Handler": "r#cdu",
        "Data": []
    }

    RestPuffle = {
        "Handler": "p#pr",
        "Data": [XTData("PuffleId", int)]
    }

    TreatPuffle = {
        "Handler": "p#pt",
        "Data": [XTData("PuffleId", int), XTData("TreatId", int)]
    }

    FeedPuffle = {
        "Handler": "p#pf",
        "Data": [XTData("PuffleId", int)]
    }

    BathPuffle = {
        "Handler": "p#pb",
        "Data": [XTData("PuffleId", int)]
    }

    PuffleInitInteractionPlay = {
        "Handler": "p#pip",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    PuffleInitInteractionRest = {
        "Handler": "p#pir",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    InteractionPlay = {
        "Handler": "p#ip",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    InteractionRest = {
        "Handler": "p#ir",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    InteractionFeed = {
        "Handler": "p#if",
        "Data": [XTData("PuffleId", int), XTData("X", int), XTData("Y", int)]
    }

    OpenBook = {
        "Handler": "t#at",
        "Data": [VariableXTData("Discard")]
    }

    CloseBook = {
        "Handler": "t#rt",
        "Data": [VariableXTData("Discard")]
    }

    BanPlayer = {
        "Handler": "o#b",
        "Data": [XTData("PlayerId", int), XTData("Message", str)]
    }

    MutePlayer = {
        "Handler": "o#m",
        "Data": [XTData("PlayerId", int)]
    }

    KickPlayer = {
        "Handler": "o#k",
        "Data": [XTData("PlayerId", int)]
    }

    GetTablePopulation = {
        "Handler": "a#gt",
        "Data": [VariableXTData("Tables")]
    }

    JoinTable = {
        "Handler": "a#jt",
        "Data": [XTData("TableId", int)]
    }

    LeaveTable = {
        "Handler": "a#lt",
        "Data": []
    }

    MovePuck = {
        "Handler": "m",
        "Data": [XTData("PlayerId", int), XTData("X", int), XTData("Y", int),
                 XTData("SpeedX", int), XTData("SpeedY", int)]
    }

    GetGame = {
        "Handler": "gz",
        "Data": [VariableXTData("Null")]
    }

    UpdateGame = {
        "Handler": "uz",
        "Data": [VariableXTData("Null")]
    }

    JoinGame = {
        "Handler": "jz",
        "Data": [VariableXTData("Null")]
    }

    SendMove = {
        "Handler": "zm",
        "Data": [VariableXTData("Move")]
    }

    GameOver = {
        "Handler": "zo",
        "Data": [XTData("Score", int)]
    }

    GetWaddlePopulation = {
        "Handler": "gw",
        "Data": [VariableXTData("Waddles")]
    }

    JoinWaddle = {
        "Handler": "jw",
        "Data": [XTData("WaddleId", int)]
    }

    LeaveWaddle = {
        "Handler": "lw",
        "Data": [VariableXTData("Null")]
    }

    ChangeDifficulty = {
        "Handler": "zd",
        "Data": [XTData("Difficulty", int)]
    }

    GetGameAgain = {
        "Handler": "zr",
        "Data": [VariableXTData("Null")]
    }

    LeaveGame = {
        "Handler": "lz",
        "Data": [VariableXTData("Null")]
    }

    CardGameOver = {
        "Handler": "czo",
        "Data": [XTData("Whatever", int)]
    }

    GetNinjaRanks = {
        "Handler": "ni#gnr",
        "Data": [XTData("PlayerId", int)]
    }

    GetNinjaLevel = {
        "Handler": "ni#gnl",
        "Data": []
    }

    GetNinjaFireLevel = {
        "Handler": "ni#gfl",
        "Data": []
    }

    GetNinjaWaterLevel = {
        "Handler": "ni#gwl",
        "Data": []
    }

    GetCards = {
        "Handler": "ni#gcd",
        "Data": []
    }

    JoinMatchMaking = {
        "Handler": "jmm",
        "Data": [VariableXTData("Null")]
    }

    LeaveMatchMaking = {
        "Handler": "lmm",
        "Data": [VariableXTData("Null")]
    }

    JoinSensei = {
        "Handler": "jsen",
        "Data": [VariableXTData("Null")]
    }

    JoinRedemption = {
        "Handler": "rjs",
        "Data": [XTData("ID", int), XTData("LoginKey", str), XTData("Language", str)]
    }

    SendCode = {
        "Handler": "rsc",
        "Data": [XTData("Code", str)]
    }

    SendGoldenChoice = {
        "Handler": "rsgc",
        "Data": [XTData("Code", str), XTData("Choice", int)]
    }


class HandlerEvent(object):

    def __init__(self, handlerDetails):
        self.handlerDetails = handlerDetails

    def __add__(self, handlerMethod):
        handlerId = self.handlerDetails["Handler"]
        handlerData = self.handlerDetails["Data"]

        XT = "#" in handlerId or handlerData and isinstance(handlerData[0], XTData)
        handlersCollection = Handlers.XTHandlers if XT else Handlers.XMLHandlers
        handlerListener = XTListener if XT else XMLListener

        # User tried to register a handler for a packet that does that pertain to this server.
        # e.g. trying to register a j#js handler on the login server
        if handlerId not in handlersCollection:
            return

        listenerObject = handlerListener(self.handlerDetails, handlerMethod)
        handlersCollection[handlerId].append(listenerObject)

        return self

    def __sub__(self, handlerMethod):
        handlerId = self.handlerDetails["Handler"]
        handlerData = self.handlerDetails["Data"]

        XT = "#" in handlerId or handlerData and isinstance(handlerData[0], XTData)
        handlersCollection = Handlers.XTHandlers if XT else Handlers.XMLHandlers

        for handlerListener in handlersCollection[handlerId]:
            if handlerListener.function == handlerMethod:
                handlersCollection[handlerId].remove(handlerListener)

        return self

class HandlersMeta(type):
    def __getattr__(self, handlerAttribute):
        if hasattr(XML, handlerAttribute):
            handlerDetails = getattr(XML, handlerAttribute)
        elif hasattr(XT, handlerAttribute):
            handlerDetails = getattr(XT, handlerAttribute)
        else:
            raise AttributeError("%r is not a valid handler." % handlerAttribute)

        return HandlerEvent(handlerDetails)

# TODO implement PossibleXTData/PossibleXMLData?
class Handlers:
    __metaclass__ = HandlersMeta
    XTHandlers = {}
    XMLHandlers = {}
    Throttles = {}

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
    @retryableTransaction()
    def HandleXT(clientObject, packetId, packetData):
        xtListeners = Handlers.XTHandlers[packetId]
        xtHandlerDataStructure = xtListeners[0].handler["Data"]
        xtData = Data()

        if clientObject.user is None:
            return False

        # TODO: Catch IndexError exceptions
        if xtHandlerDataStructure:
            dataIndex = 4

            if not isinstance(xtHandlerDataStructure[0], VariableXTData):
                for xtHandlerDataObject in xtHandlerDataStructure:
                    xtHandlerDataObjectValue = packetData[dataIndex]

                    if xtHandlerDataObject.type is int:
                        if not xtHandlerDataObjectValue.lstrip("-").isdigit():
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
                if clientObject.session.dirty:
                    clientObject.session.commit()
        except StandardError:
            clientObject.logger.exception("Uh oh! Caught potentially fatal error.")

    @staticmethod
    def Handle(handler):
        def handlerFunction(function):
            handlerId = handler["Handler"]
            handlerData = handler["Data"]

            XT = "#" in handlerId or handlerData and (isinstance(handlerData[0], XTData)
                                                      or isinstance(handlerData[0], VariableXTData))

            handlersCollection = Handlers.XTHandlers if XT else Handlers.XMLHandlers
            handlerListener = XTListener if XT else XMLListener

            if handlerId not in handlersCollection:
                handlersCollection[handlerId] = []

            listenerObject = handlerListener(handler, function)
            handlersCollection[handlerId].append(listenerObject)

            return function

        return handlerFunction

    @staticmethod
    def Throttle(secs=1):
        def handlerFunction(function):
            def handler(penguin, data):
                Handlers.Throttles[function] = secs

                if secs == -1 and function in penguin.throttle:
                    return function

                if function not in penguin.throttle:
                    penguin.throttle[function] = time.time() - secs

                lastSent = penguin.throttle[function]

                if time.time() < lastSent + Handlers.Throttles[function]:
                    return function

                function(penguin, data)
                penguin.throttle[function] = time.time()

                return function
            return handler
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
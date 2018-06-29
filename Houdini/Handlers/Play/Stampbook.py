from Houdini import Cache
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Stamp import Stamp, CoverStamp

from twisted.internet.defer import inlineCallbacks, returnValue

from sqlalchemy.sql import select

@Cache("houdini.book")
def getBookCoverString(self, penguinId, coverString = None):
    if coverString is not None:
        return coverString
    return createBookCoverString(self, penguinId)

@inlineCallbacks
def createBookCoverString(self, penguinId):
    if penguinId in self.server.players:
        player = self.server.players[penguinId]
        coverDetails = (player.user.BookColor, player.user.BookHighlight, player.user.BookPattern, player.user.BookIcon)
    else:
        coverDetails = yield self.engine.first(select([Penguin.c.BookColor, Penguin.c.BookHighlight,
                                                        Penguin.c.BookPattern, Penguin.c.BookIcon])
                                   .where(Penguin.c.ID == penguinId))

    if coverDetails is None:
        returnValue(str())

    bookColor, bookHighlight, bookPattern, bookIcon = coverDetails
    coverStamps = yield self.engine.fetchall(CoverStamp.select(CoverStamp.c.PenguinID == penguinId))

    stampsString = "%".join(["{}|{}|{}|{}|{}|{}".format(stamp.Type, stamp.Stamp, stamp.X, stamp.Y, stamp.Rotation,
                                                       stamp.Depth) for stamp in coverStamps])

    coverString =  "%".join(map(str, [bookColor, bookHighlight, bookPattern, bookIcon, stampsString]))
    getBookCoverString.invalidate(self, penguinId)
    cachedCoverString = getBookCoverString(self, penguinId, coverString)
    returnValue(cachedCoverString)

@Cache("houdini.stamps")
def getStampsString(self, penguinId, stamps = None):
    if penguinId in self.server.players:
        stamps = self.server.players[penguinId].stamps
    if stamps is not None:
        return "|".join(map(str, stamps))
    return createStampsString(self, penguinId)

@inlineCallbacks
def createStampsString(self, penguinId):
    stamps = [stampId for stampId, in (yield self.engine.fetchall(select([Stamp.c.Stamp])
                                                      .where(Stamp.c.PenguinID == penguinId)))]
    getStampsString.invalidate(self, penguinId)
    cachedStampsString = getStampsString(self, penguinId, stamps)
    returnValue(cachedStampsString)


def giveMascotStamp(self):
    for roomPlayer in self.room.players:
        if roomPlayer.user.MascotStamp:
            self.addStamp(roomPlayer.user.MascotStamp, True)
    if self.user.MascotStamp:
        for roomPlayer in self.room.players:
            roomPlayer.addStamp(self.user.MascotStamp, True)


@Handlers.Handle(XT.StampAdd)
def handleStampAdd(self, data):
    if data.StampId not in self.server.stamps:
        return

    self.addStamp(data.StampId)


@Handlers.Handle(XT.GetBookCover)
@inlineCallbacks
def handleGetBookCover(self, data):
    coverString = yield getBookCoverString(self, data.PlayerId)
    self.sendXt("gsbcd", coverString)


@Handlers.Handle(XT.GetStamps)
@inlineCallbacks
def handleGetStamps(self, data):
    stampsString = yield getStampsString(self, data.PlayerId)
    self.sendXt("gps", data.PlayerId, stampsString)


@Handlers.Handle(XT.GetRecentStamps)
def handleGetRecentStamps(self, data):
    self.sendXt("gmres", "|".join(map(str, self.recentStamps)))
    self.recentStamps = []
    self.engine.execute(Stamp.update().where(
        (Stamp.c.PenguinID == self.user.ID) & (Stamp.c.Recent == 1)).values(Recent=False))


@Handlers.Handle(XT.UpdateBookCover)
@Handlers.Throttle()
@inlineCallbacks
def handleUpdateBookCover(self, data):
    if not 4 <= len(data.StampCover) <= 10:
        return

    yield self.engine.execute(CoverStamp.delete().where(CoverStamp.c.PenguinID == self.user.ID))
    bookCover = data.StampCover[0:4]
    color, highlight, pattern, icon = bookCover
    if not(1 <= int(color) <= 6 and 1 <= int(highlight) <= 18 and
           0 <= int(pattern) <= 6 and 1 <= int(icon) <= 6):
        return

    stampTracker = []
    inventoryTracker = []
    coverStamps = []
    for stamp in data.StampCover[4:10]:
        stampArray = stamp.split("|")
        if len(stampArray) != 6:
            return
        stampType, stampId, posX, posY, rotation, depth = map(int, stampArray)
        if stampType == 0:
            if stampId in stampTracker or stampId not in self.stamps:
                return
            stampTracker.append(stampId)
        elif stampType == 1 or stampType == 2:
            if (stampId in inventoryTracker or stampId not in self.inventory or
                    (stampType == 1 and not self.server.items.isItemPin(stampId)) or
                    (stampType == 2 and not self.server.items.isItemAward(stampId))):
                return
            inventoryTracker.append(stampId)

        if not (0 <= stampType <= 2 and 0 <= posX <= 600 and 0 <= posY <= 600 and
                0 <= rotation <= 360 and 0 <= depth <= 100):
            return
        coverStamps.append({"PenguinID":self.user.ID, "Stamp":stampId, "Type":stampType, "X":posX,
                            "Y":posY, "Rotation":rotation, "Depth":depth})

    if coverStamps:
        yield self.engine.execute(CoverStamp.insert(), coverStamps)

    self.user.BookColor = color
    self.user.BookHighlight = highlight
    self.user.BookPattern = pattern
    self.user.BookIcon = icon
    self.user.BookModified = 1

    getBookCoverString.invalidate(self, self.user.ID)

from beaker.cache import cache_region as Cache, region_invalidate as Invalidate

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Stamp import Stamp, CoverStamp


@Cache("houdini", "book")
def getBookCoverString(self, penguinId):
    if penguinId in self.server.players:
        player = self.server.players[penguinId]
        coverDetails = (player.user.BookColor, player.user.BookHighlight, player.user.BookPattern, player.user.BookIcon)
    else:
        coverDetails = self.session.query(Penguin.BookColor, Penguin.BookHighlight, Penguin.BookPattern,
                                          Penguin.BookIcon).filter_by(ID=penguinId).first()

    if coverDetails is None:
        return str()

    bookColor, bookHighlight, bookPattern, bookIcon = coverDetails
    coverStamps = self.session.query(CoverStamp).filter_by(PenguinID=penguinId)

    coverString = "%".join(["{}|{}|{}|{}|{}|{}".format(stamp.Type, stamp.Stamp, stamp.X, stamp.Y, stamp.Rotation,
                                                       stamp.Depth) for stamp in coverStamps])

    return "%".join(map(str, [bookColor, bookHighlight, bookPattern, bookIcon, coverString]))


@Cache("houdini", "stamps")
def getStampsString(self, penguinId):
    stamps = self.stamps if penguinId == self.user.ID else \
        [stampId for stampId, in self.session.query(Stamp.Stamp).filter_by(PenguinID=penguinId)]
    return "|".join(map(str, stamps))


def giveMascotStamp(self):
    for roomPlayer in self.room.players:
        if roomPlayer.user.MascotStamp and self.user.Moderator != 2:
            self.addStamp(roomPlayer.user.MascotStamp, True)
    if self.user.MascotStamp and self.user.Moderator != 2:
        for roomPlayer in self.room.players:
            roomPlayer.addStamp(self.user.MascotStamp, True)


@Handlers.Handle(XT.StampAdd)
def handleStampAdd(self, data):
    if data.StampId not in self.server.stamps:
        return

    self.addStamp(data.StampId)


@Handlers.Handle(XT.GetBookCover)
def handleGetBookCover(self, data):
    self.sendXt("gsbcd", getBookCoverString(self, data.PlayerId))


@Handlers.Handle(XT.GetStamps)
def handleGetStamps(self, data):
    self.sendXt("gps", data.PlayerId, getStampsString(self, data.PlayerId))


@Handlers.Handle(XT.GetRecentStamps)
def handleGetRecentStamps(self, data):
    self.sendXt("gmres", "|".join(map(str, self.recentStamps)))
    self.recentStamps = []
    self.session.query(Stamp).filter_by(PenguinID=self.user.ID, Recent=1)\
        .update({"Recent": False})


@Handlers.Handle(XT.UpdateBookCover)
@Handlers.Throttle()
def handleUpdateBookCover(self, data):
    if not 4 <= len(data.StampCover) <= 10:
        return

    self.session.query(CoverStamp).filter_by(PenguinID=self.user.ID).delete()
    bookCover = data.StampCover[0:4]
    color, highlight, pattern, icon = bookCover
    if not(1 <= int(color) <= 6 and 1 <= int(highlight) <= 18 and
           0 <= int(pattern) <= 6 and 1 <= int(icon) <= 6):
        return

    stampTracker = []
    inventoryTracker = []
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

        self.session.add(CoverStamp(PenguinID=self.user.ID, Stamp=stampId, Type=stampType, X=posX,
                                    Y=posY, Rotation=rotation, Depth=depth))

    self.user.BookColor = color
    self.user.BookHighlight = highlight
    self.user.BookPattern = pattern
    self.user.BookIcon = icon
    self.user.BookModified = 1

    Invalidate(getBookCoverString, 'houdini', 'book', self.user.ID)

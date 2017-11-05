from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.StampAdd)
def handleStampAdd(self, data):
    if data.StampId not in self.server.stamps:
        return

    self.addStamp(data.StampId)

@Handlers.Handle(XT.GetBookCover)
def handleGetBookCover(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gsbcd", self.user.StampBook)
    else:
        player = self.session.query(Penguin.StampBook).\
            filter(Penguin.ID == data.PlayerId).first()

        if player is None:
            return self.transport.loseConnection()

        self.sendXt("gsbcd", player.StampBook)

@Handlers.Handle(XT.GetStamps)
def handleGetStamps(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gps", data.PlayerId, self.user.Stamps)
    else:
        player = self.session.query(Penguin.Stamps).\
            filter(Penguin.ID == data.PlayerId).first()

        if player is None:
            return self.transport.loseConnection()

        self.sendXt("gps", data.PlayerId, player.Stamps)

@Handlers.Handle(XT.GetRecentStamps)
def handleGetRecentStamps(self, data):
    self.sendXt("gmres", self.user.RecentStamps)
    self.user.RecentStamps = ""
    self.session.commit()

@Handlers.Handle(XT.UpdateBookCover)
def handleUpdateBookCover(self, data):
    if not 4 <= len(data.StampCover) <= 10:
        return
    bookCover = data.StampCover[0:4]
    color, highlight, pattern, icon = bookCover
    if not(1 <= int(color) <= 6 and 1 <= int(highlight) <= 18 \
        and -1 <= int(pattern) <= 6 and 1 <= int(icon) <= 6):
        return
    for stamp in data.StampCover[4:10]:
        stampArray = stamp.split("|")
        if len(stampArray) != 6:
            return
        stampType, stampId, posX, posY, rotation, depth = stampArray
        stamps = self.user.Stamps.split("|")
        if stampId not in stamps:
            return
        if not (0 <= int(stampType) <= 2 and 0 <= int(posX) <= 600 \
                and 0 <= int(posY) <= 600 and 0 <= int(rotation) <= 360 \
                and 0 <= int(depth) <= 100):
            return
        bookCover.append(stamp)
    self.user.StampBook = "%".join(bookCover)
    self.session.commit()

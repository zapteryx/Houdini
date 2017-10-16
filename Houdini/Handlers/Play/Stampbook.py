from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from sqlalchemy.orm import load_only

@Handlers.Handle(XT.StampAdd)
def handleStampAdd(self, data):
    self.addStamp(data.StampId)

@Handlers.Handle(XT.GetBookCover)
def handleGetBookCover(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gsbcd", self.user.StampBook)
    else:
        player = self.session.query(Penguin).\
            filter(Penguin.ID == data.PlayerId).\
            option(load_only("StampBook")).first()

        if player is None:
            return self.transport.loseConnection()

        self.sendXt("gsbcd", player.StampBook)

@Handlers.Handle(XT.GetStamps)
def handleGetStamps(self, data):
    if data.PlayerId == self.user.ID:
        self.sendXt("gps", data.PlayerId, self.user.Stamps)
    else:
        player = self.session.query(Penguin).\
            filter(Penguin.ID == data.PlayerId).\
            option(load_only("Stamps")).first()

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
    bookCover = data.StampCover[0:4]
    color, highlight, pattern, icon = bookCover
    if 1 <= int(color) <= 6 \
        and 1 <= int(highlight) <= 18 \
        and -1 <= int(pattern) <= 6 \
        and 1 <= int(icon) <= 6:
        for stamp in data.StampCover[4:10]:
            stampType, stampId, posX, posY, rotation, depth = stamp.split("|")
            stamps = self.user.Stamps.split("|")
            if stampId not in stamps:
                return
            if 0 <= int(stampType) <= 2 \
                    and 0 <= int(posX) <= 600 \
                    and 0 <= int(posY) <= 600 \
                    and 0 <= int(rotation) <= 360 \
                    and 0 <= int(depth) <= 100:
                bookCover.append(stamp)
        self.user.StampBook = "%".join(bookCover)
        self.session.commit()

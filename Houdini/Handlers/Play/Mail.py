import time, random, datetime
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Postcard import Postcard
from Houdini.Data.Penguin import Penguin, IgnoreList

from twisted.internet.defer import inlineCallbacks, returnValue

from sqlalchemy.sql import select, func

@Handlers.Handle(XT.StartMailEngine)
@Handlers.Throttle(-1)
@inlineCallbacks
def handleStartMailEngine(self, data):
    postcards = []
    if not self.user.AgentStatus and random.random() < 0.4:
        epfInvited = yield self.engine.first(Postcard.select(
            (Postcard.c.RecipientID == self.user.ID) &
            ((Postcard.c.Type == '112') | (Postcard.c.Type == '47'))))
        if not epfInvited:
            postcards.append({"RecipientID": self.user.ID, "SenderID": None, "Details": "", "Type": 112})

    lastPaycheck = self.user.LastPaycheck.date()
    if lastPaycheck == 0:
        lastPaycheck = datetime.date.today()
    today = datetime.date.today()
    firstDayOfMonth = today.replace(day=1)
    lastPaycheck = lastPaycheck.replace(day=1)
    while lastPaycheck < firstDayOfMonth:
        lastPaycheck = lastPaycheck + datetime.timedelta(days=32)
        lastPaycheck = lastPaycheck.replace(day=1)
        sendDate = lastPaycheck + datetime.timedelta(days=1)
        if 428 in self.inventory:
            postcards.append({"RecipientID": self.user.ID, "SenderID": None, "Details": "",
                              "SendDate": sendDate, "Type": 172})
            self.user.Coins += 250
        if self.user.AgentStatus:
            postcards.append({"RecipientID": self.user.ID, "SenderID": None, "Details": "",
                              "SendDate": sendDate, "Type": 184})
            self.user.Coins += 350
    self.user.LastPaycheck = lastPaycheck

    if postcards:
        yield self.engine.execute(Postcard.insert(), postcards)

    totalMail = yield self.engine.scalar(select([func.count()]).select_from(
        Postcard).where(Postcard.c.RecipientID == self.user.ID))
    unreadMail = yield self.engine.scalar(select([func.count()]).select_from(Postcard).where(
        (Postcard.c.RecipientID == self.user.ID) & (Postcard.c.HasRead == 0)))

    self.sendXt("mst", unreadMail, totalMail)


@Handlers.Handle(XT.GetMail)
@Handlers.Throttle(-1)
@inlineCallbacks
def handleGetMail(self, data):
    mailbox = yield self.engine.fetchall(select([Postcard, Penguin.c.Nickname]).select_from(
        Postcard.join(Penguin, Penguin.c.ID == Postcard.c.SenderID, isouter=True)).where(
        Postcard.c.RecipientID == self.user.ID).order_by(Postcard.c.SendDate.desc()))

    postcardArray = []
    for postcardId, senderId, recipientId, type, sendDate, details, hasRead, penguinName in mailbox:
        penguinName, senderId = ("sys", 0) if senderId is None else (penguinName, senderId)
        unixSendDate = int(time.mktime(sendDate.timetuple()))
        postcardArray.append("|".join([penguinName, str(senderId),
                                       str(type), details, str(unixSendDate),
                                       str(postcardId), str(int(hasRead))]))
    postcardString = "%".join(postcardArray)
    self.sendXt("mg", postcardString)


@Handlers.Handle(XT.SendMail)
@Handlers.Throttle(2)
@inlineCallbacks
def handleSendMail(self, data):
    if self.user.Coins < 10:
        self.sendXt("ms", self.user.Coins, 2)
        self.logger.info("%d tried to send postcard with insufficient funds.", self.user.ID)
        returnValue(False)
    if data.RecipientId not in self.server.players:
        ignored = yield self.engine.scalar(IgnoreList.select(
            (IgnoreList.c.PenguinID == data.RecipientId) & (IgnoreList.c.IgnoreID == self.user.ID)))
        if ignored is not None:
            returnValue(self.sendXt("ms", self.user.Coins, 1))
        player = yield self.engine.scalar(Penguin.select(Penguin.c.ID == data.RecipientId))
        if player is None:
            returnValue(False)
    elif self.user.ID in self.server.players[data.RecipientId].ignore:
        returnValue(self.sendXt("ms", self.user.Coins, 1))
    recipientMailCount = yield self.engine.scalar(select([func.count()]).select_from(
        Postcard).where(Postcard.c.RecipientID == data.RecipientId))
    if recipientMailCount >= 100:
        self.sendXt("ms", self.user.Coins, 0)
    self.user.Coins -= 10
    currentTimestamp = int(time.time())
    result = yield self.engine.execute(Postcard.insert(), RecipientID=data.RecipientId, SenderID=self.user.ID,
                        Details="", Type=data.PostcardId)
    self.sendXt("ms", self.user.Coins, 1)
    if data.RecipientId in self.server.players:
        recipientObject = self.server.players[data.RecipientId]
        recipientObject.sendXt("mr", self.user.Username, self.user.ID, data.PostcardId,
                               "", currentTimestamp, result.inserted_primary_key[0])
    self.logger.info("%d sent %d a postcard (%d).", self.user.ID, data.RecipientId,
                     data.PostcardId)


@Handlers.Handle(XT.MailChecked)
def handleMailChecked(self, data):
    self.engine.execute(Postcard.update().where(
        Postcard.c.RecipientID == self.user.ID).values(HasRead=True))


@Handlers.Handle(XT.DeleteMail)
def handleDeleteMail(self, data):
    self.engine.execute(Postcard.delete().where(
        (Postcard.c.RecipientID == self.user.ID) & (Postcard.c.ID == data.PostcardId)))


@Handlers.Handle(XT.DeleteMailFromUser)
@inlineCallbacks
def handleDeleteMailFromUser(self, data):
    senderId = None if data.SenderId == 0 else data.SenderId
    self.engine.execute(Postcard.delete().where(
        (Postcard.c.RecipientID == self.user.ID) & (Postcard.c.SenderID == senderId)))
    totalMail = yield self.engine.scalar(select([func.count()]).select_from(
        Postcard).where(Postcard.c.RecipientID == self.user.ID))
    self.sendXt("mdp", totalMail)

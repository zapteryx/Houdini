import time, random, datetime
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Postcard import Postcard
from Houdini.Data.Penguin import Penguin, IgnoreList
from Houdini.Data import retryableTransaction

@Handlers.Handle(XT.StartMailEngine)
@Handlers.Throttle(-1)
def handleStartMailEngine(self, data):
    if not self.user.AgentStatus and random.random() < 0.4:
        epfInvited = self.session.query(Postcard).filter(Postcard.RecipientID == self.user.ID). \
            filter((Postcard.Type == '112') | (Postcard.Type == '47')).first()
        if not epfInvited:
            postcard = Postcard(RecipientID=self.user.ID, SenderID=None,
                                Details="", Type=112)
            self.session.add(postcard)

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
            postcard = Postcard(RecipientID=self.user.ID, SenderID=None,
                                Details="", SendDate=sendDate, Type=172)
            self.session.add(postcard)
            self.user.Coins += 250
        if self.user.AgentStatus:
            postcard = Postcard(RecipientID=self.user.ID, SenderID=None,
                                Details="", SendDate=sendDate, Type=184)
            self.session.add(postcard)
            self.user.Coins += 350
    self.user.LastPaycheck = lastPaycheck

    totalMail = self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID).count()
    unreadMail = self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID). \
        filter(Postcard.HasRead == 0).count()

    self.sendXt("mst", unreadMail, totalMail)


@Handlers.Handle(XT.GetMail)
@Handlers.Throttle(-1)
@retryableTransaction()
def handleGetMail(self, data):
    mailbox = self.session.query(Postcard, Penguin.Nickname) \
        .join(Penguin, Penguin.ID == Postcard.SenderID, isouter=True) \
        .filter(Postcard.RecipientID == self.user.ID)\
        .order_by(Postcard.SendDate.desc())
    postcardArray = []
    for postcard, penguinName in mailbox:
        penguinName, senderId = ("sys", 0) if postcard.SenderID is None else (penguinName, postcard.SenderID)
        unixSendDate = int(time.mktime(postcard.SendDate.timetuple()))
        postcardArray.append("|".join([penguinName, str(senderId),
                                       str(postcard.Type), postcard.Details, str(unixSendDate),
                                       str(postcard.ID), str(int(postcard.HasRead))]))
    postcardString = "%".join(postcardArray)
    self.sendXt("mg", postcardString)
    self.session.commit()


@Handlers.Handle(XT.SendMail)
@Handlers.Throttle(2)
@retryableTransaction()
def handleSendMail(self, data):
    if self.user.Coins < 10:
        self.sendXt("ms", self.user.Coins, 2)
        self.logger.info("%d tried to send postcard with insufficient funds.", self.user.ID)
        return
    if data.RecipientId not in self.server.players:
        Ignored = self.session.query(IgnoreList) \
            .filter_by(PenguinID=data.RecipientId, IgnoreID=self.user.ID).scalar()
        if Ignored is not None:
            return self.sendXt("ms", self.user.Coins, 1)
        player = self.session.query(Penguin).filter_by(ID=data.RecipientId).scalar()
        if player is None:
            return
    elif self.user.ID in self.server.players[data.RecipientId].ignore:
        return self.sendXt("ms", self.user.Coins, 1)
    recipientMailCount = self.session.query(Postcard). \
        filter(Postcard.RecipientID == data.RecipientId).count()
    if recipientMailCount >= 100:
        self.sendXt("ms", self.user.Coins, 0)
    self.user.Coins -= 10
    currentTimestamp = int(time.time())
    postcard = Postcard(RecipientID=data.RecipientId, SenderID=self.user.ID,
                        Details="", Type=data.PostcardId)
    self.session.add(postcard)
    self.session.commit()
    self.sendXt("ms", self.user.Coins, 1)
    if data.RecipientId in self.server.players:
        recipientObject = self.server.players[data.RecipientId]
        recipientObject.sendXt("mr", self.user.Username, self.user.ID, data.PostcardId,
                               "", currentTimestamp, postcard.ID)
    self.logger.info("%d sent %d a postcard (%d).", self.user.ID, data.RecipientId,
                     data.PostcardId)


@Handlers.Handle(XT.MailChecked)
def handleMailChecked(self, data):
    self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID). \
        update({"HasRead": True})


@Handlers.Handle(XT.DeleteMail)
def handleDeleteMail(self, data):
    self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID). \
        filter(Postcard.ID == data.PostcardId).delete()


@Handlers.Handle(XT.DeleteMailFromUser)
def handleDeleteMailFromUser(self, data):
    senderId = None if data.SenderId == 0 else data.SenderId
    self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID). \
        filter(Postcard.SenderID == senderId).delete()
    totalMail = self.session.query(Postcard). \
        filter(Postcard.RecipientID == self.user.ID).count()
    self.sendXt("mdp", totalMail)

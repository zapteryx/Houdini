import time
import random
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Mail import Mail
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.StartMailEngine)
def handleStartMailEngine(self, data):
    totalMail = self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID).count()
    unreadMail = self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID).\
        filter(Mail.HasRead == False).count()

    """
    In AS2 EPF you were'nt automatically invited to EPF,
    you had to have the postcard (either randomly from
    system or from another player) so lets send EPF invites
    randomly (40% probability)
    """
    if random.random() < 0.4:
        q = self.session.query(Mail).filter(Mail.Recipient == self.user.ID).\
            filter((Mail.Type == '112') | (Mail.Type == '47'))
        epfInvited = self.session.query(q.exists()).scalar()
        if not epfInvited:
            postcard = Mail(Recipient=self.user.ID, SenderName="sys",
                            SenderID=0, Details="", Date=int(time.time()),
                            Type=112)
            self.session.add(postcard)
            self.session.commit()

    self.sendXt("mst", unreadMail, totalMail)

@Handlers.Handle(XT.GetMail)
def handleGetMail(self, data):
    mailbox = self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID)
    postcardArray = []
    for postcard in mailbox:
        postcardArray.append("|".join([postcard.SenderName, str(postcard.SenderID),
                                       str(postcard.Type), postcard.Details, str(postcard.Date),
                                       str(postcard.ID), str(int(postcard.HasRead))]))
    postcardString = "%".join(postcardArray)
    self.sendXt("mg", postcardString)

@Handlers.Handle(XT.SendMail)
def handleSendMail(self, data):
    q = self.session.query(Penguin).filter(Penguin.ID == data.RecipientId)
    recipientExists = self.session.query(q.exists()).scalar()
    if not recipientExists:
        return
    if self.user.Coins < 10:
        self.sendXt("ms", self.user.Coins, 2)
        self.logger.debug("%d tried to send postcard with insufficient funds.", self.user.ID)
        return
    recipientMailCount = self.session.query(Mail).\
        filter(Mail.Recipient == data.RecipientId).count()
    if recipientMailCount >= 100:
        self.sendXt("ms", self.user.Coins, 0)
    self.user.Coins -= 10
    currentTimestamp = int(time.time())
    postcard = Mail(Recipient=data.RecipientId, SenderName=self.user.Username,
           SenderID=self.user.ID, Details="", Date=currentTimestamp,
           Type=data.PostcardId)
    self.session.add(postcard)
    self.session.commit()
    self.sendXt("ms", self.user.Coins, 1)
    if data.RecipientId in self.server.players:
        recipientObject = self.server.players[data.RecipientId]
        recipientObject.sendXt("mr", self.user.Username, self.user.ID, data.PostcardId,
                               "", currentTimestamp, postcard.ID)
    self.logger.info("%d send %d a postcard (%d).", self.user.ID, data.RecipientId,
                     data.PostcardId)

@Handlers.Handle(XT.MailChecked)
def handleMailChecked(self, data):
    self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID).\
        update({"HasRead": True})
    self.session.commit()

@Handlers.Handle(XT.DeleteMail)
def handleDeleteMail(self, data):
    self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID).\
        filter(Mail.ID == data.PostcardId).delete()
    self.session.commit()

@Handlers.Handle(XT.DeleteMailFromUser)
def handleDeleteMailFromUser(self, data):
    self.session.query(Mail).\
        filter(Mail.Recipient == self.user.ID).\
        filter(Mail.SenderID == data.SenderId).delete()
    self.session.commit()
    totalMail = self.session.query(Mail). \
        filter(Mail.Recipient == self.user.ID).count()
    self.sendXt("mdp", totalMail)
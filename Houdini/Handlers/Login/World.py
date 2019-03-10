from datetime import datetime
from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XML
from Houdini.Data.Login import Login
from Houdini.Data.Ban import Ban
from Houdini.Data.Stamp import Stamp
from Houdini.Data.Penguin import Penguin, BuddyList, IgnoreList, IglooInventory, \
    FurnitureInventory, FloorInventory, LocationInventory, Inventory
from Houdini.Data.Igloo import Igloo, IglooLike
from Houdini.Data.Puffle import Puffle, CareInventory, PuffleQuest
from Houdini.Data.Deck import Deck
from Houdini.Data.Membership import Membership
from Houdini.Crypto import Crypto
from Houdini.Data import retryableTransaction
from Houdini.Handlers.Play.Navigation import RoomFieldKeywords, Room

@Handlers.Handle(XML.Login)
@retryableTransaction()
def handleLogin(self, data):
    rawLoginData = data.Username
    passwordHashes = data.Password

    playerId, _, swid, loginKey, _, languageApproved, languageRejected = rawLoginData.split("|")
    clientLoginKey, confirmationHash = passwordHashes.split("#")

    self.logger.info("{} is attempting to login..".format(playerId))

    self.session.commit()
    user = self.session.query(Penguin).filter_by(ID=playerId).first()
    membership = self.session.query(Membership).filter_by(PenguinID=playerId).first()

    user.Approval = languageApproved

    user.Member = membership.Status
    user.MembershipDays = membership.CumulativeDays

    if user.Moderator == 0:
        user.maxCoins = 1000000
    else:
        user.maxCoins = 10000000

    if user.Coins > user.maxCoins:
        user.Coins = user.maxCoins

    if user.Member == 0:
        user.MembershipLeft = None
    else:
        membershipEnd = datetime.strptime(str(membership.End), "%Y-%m-%d %H:%M:%S")
        membershipLeft = membershipEnd - datetime.utcnow()
        user.MembershipLeft = round(membershipLeft.days + (float(membershipLeft.seconds) / 86400),1)

    if user is None:
        return self.sendErrorAndDisconnect(100)

    # TODO: Perform more validation checks
    # i.e. checking to make sure that the login key sent by the server matches the one in the rawLoginData variable
    # and check confirmationHash

    if not user.LoginKey:
        return self.transport.loseConnection()

    loginHash = Crypto.encryptPassword(user.LoginKey + self.randomKey) + user.LoginKey

    if clientLoginKey != loginHash:
        self.logger.info("{} failed to login.".format(user.Username))

        return self.sendErrorAndDisconnect(101)

    if user.Permaban:
        return self.transport.loseConnection()

    currentDateTime = datetime.now()

    activeBan = self.session.query(Ban).filter(Ban.PenguinID == user.ID)\
        .filter(Ban.Expires >= currentDateTime).first()

    if activeBan is not None:
        return self.transport.loseConnection()

    if user.ID in self.server.players:
        self.server.players[user.ID].transport.loseConnection()

    self.logger.info("{} logged in successfully".format(user.Username))

    self.session.add(user)
    self.user = user
    self.user.OnlineStatus = self.server.serverId

    ipAddr = self.transport.getPeer().host

    self.login = Login(PenguinID=self.user.ID, Date=datetime.now(), IPAddress=ipAddr)

    # Add them to the Redis set
    self.server.redis.sadd("%s.players" % self.server.serverName, self.user.ID)
    self.server.redis.incr("%s.population" % self.server.serverName)

    self.sendXt("l")

    self.age = (currentDateTime - self.user.RegistrationDate).days

    stampQuery = self.session.query(Stamp.Stamp).filter_by(PenguinID=self.user.ID)
    self.stamps = [stampId for stampId, in stampQuery]
    self.recentStamps = [stampId for stampId, in stampQuery.filter_by(Recent=1)]

    self.requests = {buddyId: buddyNickname for buddyId, buddyNickname in
                    self.session.query(BuddyList.BuddyID, Penguin.Nickname).
                    join(Penguin, Penguin.ID == BuddyList.BuddyID).
                    filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 0))}

    self.buddies = {buddyId: buddyNickname for buddyId, buddyNickname in
                    self.session.query(BuddyList.BuddyID, Penguin.Nickname).
                    join(Penguin, Penguin.ID == BuddyList.BuddyID).
                    filter(BuddyList.PenguinID == self.user.ID).
                    filter(or_(BuddyList.Type == 1,BuddyList.Type == 2))}

    self.bestBuddies = [buddyId for buddyId, in self.session.query(BuddyList.BuddyID).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
                     filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 2))]

    self.characterBuddies = [characterId for characterId, in self.session.query(BuddyList.BuddyID).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
                     filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 3))]

    self.ignore = {ignoreId: ignoreNickname for ignoreId, ignoreNickname in
                   self.session.query(IgnoreList.IgnoreID, Penguin.Nickname).
                   join(Penguin, Penguin.ID == IgnoreList.IgnoreID).
                   filter(IgnoreList.PenguinID == self.user.ID)}

    self.inventory = [itemId for itemId, in self.session.query(Inventory.ItemID).filter_by(PenguinID=self.user.ID)]

    self.furniture = {furnitureId: quantity for furnitureId, quantity in self.session.query(
        FurnitureInventory.FurnitureID, FurnitureInventory.Quantity).filter_by(PenguinID=self.user.ID)}

    self.floors = [floorId for floorId, in self.session.query(FloorInventory.FloorID).filter_by(PenguinID=self.user.ID)]

    self.deck = {cardId: quantity for cardId, quantity in self.session.query(
        Deck.CardID, Deck.Quantity).filter_by(PenguinID=self.user.ID)}

    self.cards = [self.server.cards[cardId] for cardId, quantity in self.deck.iteritems() for _ in xrange(quantity)]

    self.iglooInventory = [iglooId for iglooId, in self.session.query(IglooInventory.IglooID)
        .filter_by(PenguinID=self.user.ID)]

    self.igloos = {iglooId: igloo for iglooId, igloo in
                   self.session.query(Igloo.ID, Igloo).filter_by(PenguinID=self.user.ID)}
    self.session.add_all(self.igloos.values())

    self.igloo = self.session.query(Igloo).filter_by(ID=self.user.Igloo).first()
    self.likeTimers = {iglooId: likeTime for iglooId, likeTime in
                       self.session.query(IglooLike.IglooID, IglooLike.Date).filter_by(PlayerID=self.user.ID)}

    # Triggered after something like a server restart
    if self.igloo is not None and self.igloo.Locked == 0 and self.user.ID not in self.server.openIgloos:
        externalIglooId = self.user.ID + 1000
        if externalIglooId not in self.server.rooms:
            iglooFieldKeywords = RoomFieldKeywords.copy()
            iglooFieldKeywords["Id"] = externalIglooId
            iglooFieldKeywords["InternalId"] = self.user.ID
            iglooFieldKeywords["IglooId"] = self.igloo.ID

            self.server.rooms[externalIglooId] = Room(**iglooFieldKeywords)

        self.server.openIgloos[self.user.ID] = self.user.Nickname

    self.locations = [locationId for locationId, in self.session.query(LocationInventory.LocationID)
        .filter_by(PenguinID=self.user.ID)]

    self.puffles = {puffle.ID: puffle for puffle in self.session.query(Puffle).filter_by(PenguinID=self.user.ID)}
    self.session.add_all(self.puffles.values())

    self.walkingPuffle = self.session.query(Puffle) \
        .filter(Puffle.PenguinID == self.user.ID, Puffle.Walking == 1).first()

    self.careInventory = {itemId: quantity for itemId, quantity in self.session.query(
        CareInventory.ItemID, CareInventory.Quantity).filter_by(PenguinID=self.user.ID)}

    puffleQuests = self.session.query(PuffleQuest).filter(PuffleQuest.PenguinID == self.user.ID).all()

    if not puffleQuests:
        puffleQuests = []

        for taskId in range(0, 4):
            puffleQuests.append(PuffleQuest(PenguinID=self.user.ID, TaskID=taskId))

    self.session.add_all(puffleQuests)

    self.puffleQuests = {task.TaskID: task for task in puffleQuests}

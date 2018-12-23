from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, BuddyList
from Houdini.Handlers.Play.Moderation import cheatBan

@Handlers.Handle(XT.GetPendingRequests)
def handleGetPendingRequests(self, data):
    pendingRequests = []

    buddyRequests = {buddyId: buddyNickname for buddyId, buddyNickname in
                    self.session.query(BuddyList.BuddyID, Penguin.Nickname).
                    join(Penguin, Penguin.ID == BuddyList.BuddyID).
                    filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 0))}

    if len(buddyRequests):
        for buddyId, buddyNickname in buddyRequests.items():
            pendingRequests.append("{}|{}".format(buddyId, buddyNickname))

        self.sendXt("pr", *pendingRequests)

@Handlers.Handle(XT.GetBuddies)
def handleGetBuddies(self, data):
    playerBuddies = []

    acceptedBuddies = {buddyId: buddyNickname for buddyId, buddyNickname in
                    self.session.query(BuddyList.BuddyID, Penguin.Nickname).
                    join(Penguin, Penguin.ID == BuddyList.BuddyID).
                    filter(BuddyList.PenguinID == self.user.ID).
                    filter(or_(BuddyList.Type == 1,BuddyList.Type == 2))}

    if len(acceptedBuddies) > 0:
        for buddyId, buddyNickname in acceptedBuddies.items():
            status = "online" if buddyId in self.server.players else "offline"
            playerBuddies.append("{}|{}|{}|{}".format(buddyId, buddyId, buddyNickname, status))

        self.sendXt("gb", *playerBuddies)

@Handlers.Handle(XT.GetBestFriends)
def handleGetBestFriends(self, data):
    bestFriends = self.session.query(BuddyList.BuddyID).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
                     filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 2))

    if bestFriends.count() > 0:
        bestFriendsString = "%".join("{}".format(buddy.BuddyID) for buddy in bestFriends)

        self.sendXt("gbf", bestFriendsString)

@Handlers.Handle(XT.GetCharacters)
def handleGetCharacters(self, data):
    characterBuddies = self.session.query(BuddyList.BuddyID).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
                     filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.Type == 3))

    if characterBuddies.count() > 0:
        characterBuddiesString = "%".join("{}".format(buddy.BuddyID) for buddy in characterBuddies)

        self.sendXt("gc", characterBuddiesString)

@Handlers.Handle(XT.ToggleBestFriend)
def handleToggleBestFriend(self, data):
    if "character_" not in str(data.Id):

        friend = self.session.query(BuddyList.Type).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).first()

        if not friend or friend[0] == 0:
            return self.transport.loseConnection()

        type = 2 if friend[0] == 1 else 1

        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).update({"Type": type})

@Handlers.Handle(XT.BuddyRequest)
def handleBuddyRequest(self, data):
    if "|" in data.Player:
        wantedBuddyId = int(data.Player.split("|")[1])
    else:
        wantedBuddyId = int(data.Player)

    if wantedBuddyId == self.user.ID:
        # Don't let people add themselves
        return self.transport.loseConnection()

    friend = self.session.query(BuddyList.BuddyID).filter(and_(BuddyList.PenguinID == wantedBuddyId,BuddyList.BuddyID == self.user.ID)).first()

    if not friend:
        request = BuddyList(PenguinID=wantedBuddyId, BuddyID=self.user.ID, Type=0)

        self.session.add(request)
        self.session.commit()

        if wantedBuddyId in self.server.players:
            self.server.players[wantedBuddyId].sendXt("br", self.user.ID, self.server.players[self.user.ID].user.Nickname)

@Handlers.Handle(XT.CharacterRequest)
def handleCharacterRequest(self, data):
    if self.server.mascots.getMascot(data.Id):
        mascotStampId = self.session.query(Penguin.MascotStamp).filter(Penguin.ID == data.Id).first()

        if mascotStampId[0] != 0:
            if data.Id not in self.server.players and mascotStampId[0] not in self.stamps:
                # Prevent hackers from force-adding characters
                # Note that this won't work for characters without stamps
                return cheatBan(self, self.user.ID, 72, "Attempting to force-add a character to friends list")

        friend = self.session.query(BuddyList.BuddyID).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).first()

        if not friend:
            request = BuddyList(PenguinID=self.user.ID, BuddyID=data.Id, Type=3)

            self.session.add(request)
            self.session.commit()

            self.sendXt("cr", data.Id)

from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, BuddyList
from Houdini.Handlers.Play.Moderation import cheatBan

@Handlers.Handle(XT.RefreshPlayerFriendInfo)
def handleRefreshPlayerFriendInfo(self, data):
    handleGetBuddies(self, data)
    handleGetBestFriends(self, data)
    handleGetPendingRequests(self, data)
    handleGetCharacters(self, data)

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

    if wantedBuddyId in self.server.mascots:
        return self.transport.loseConnection()

    if wantedBuddyId == self.user.ID:
        # Don't let people add themselves
        return self.transport.loseConnection()

    friend = self.session.query(BuddyList.BuddyID).filter(and_(BuddyList.PenguinID == wantedBuddyId,BuddyList.BuddyID == self.user.ID)).first()

    if not friend:
        request = BuddyList(PenguinID=wantedBuddyId, BuddyID=self.user.ID, Type=0)

        self.session.add(request)
        self.session.commit()

        if wantedBuddyId in self.server.players:
            player = self.server.players[wantedBuddyId]
            player.sendXt("pr", "{}|{}".format(self.user.ID, self.server.players[self.user.ID].user.Nickname))

@Handlers.Handle(XT.CharacterRequest)
def handleCharacterRequest(self, data):
    if data.Id in self.server.mascots:
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

@Handlers.Throttle(1)
@Handlers.Handle(XT.BuddyAccept)
def handleBuddyAccept(self, data):
    if data.Id in self.server.mascots:
        return self.transport.loseConnection()

    if data.Id == self.user.ID:
        return self.transport.loseConnection()

    pendingRequest = self.session.query(BuddyList.BuddyID,Penguin.Nickname).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
            filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).first()

    if not pendingRequest:
        # Prevent hackers from adding players haven't sent requests
        return cheatBan(self, self.user.ID, 72, "Attempting to add player to friends list")

    doubleRequest = self.session.query(BuddyList.BuddyID,Penguin.Nickname).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
            filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID,BuddyList.Type == 0)).first()

    if doubleRequest:
        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID,BuddyList.Type == 0)).update({"Type": 1})
    else:
        accept = BuddyList(PenguinID=data.Id, BuddyID=self.user.ID, Type=1)
        self.session.add(accept)

    self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).update({"Type": 1})
    self.session.commit()

    status = "online" if data.Id in self.server.players else "offline"
    newBuddy = "{}|{}|{}|{}".format(data.Id, data.Id, pendingRequest[1], status)

    self.sendXt("ba", newBuddy)
    handleRefreshPlayerFriendInfo(self, data)

    if data.Id in self.server.players:
        player = self.server.players[data.Id]
        player.sendXt("ba", "{}|{}|{}|online".format(self.user.ID, self.user.ID, self.user.Nickname))
        handleRefreshPlayerFriendInfo(player, data)

@Handlers.Handle(XT.BuddyReject)
def handleBuddyReject(self, data):
    pendingRequest = self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).first()

    if pendingRequest:
        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).delete()
        self.session.commit()

        self.sendXt("rr", data.Id)

@Handlers.Handle(XT.RemoveBuddy)
def handleRemoveBuddy(self, data):
    if data.Id not in self.server.mascots:
        friend = self.session.query(BuddyList.Type).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).first()

        if friend:
            if friend[0] == 1 or friend[0] == 2:
                self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).delete()
                self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID)).delete()

                self.session.commit()

                self.sendXt("rb", data.Id)
                handleRefreshPlayerFriendInfo(self, data)

                if data.Id in self.server.players:
                    player = self.server.players[data.Id]
                    player.sendXt("rb", self.user.ID)
                    handleRefreshPlayerFriendInfo(player, data)

from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, BuddyList
from Houdini.Handlers.Play.Player import getPlayerInfo
from Houdini.Handlers.Play.Moderation import cheatBan
from Houdini.Handlers.Play.Igloo import getActiveIgloo

@Handlers.Handle(XT.RefreshPlayerFriendInfo)
def handleRefreshPlayerFriendInfo(self, data):
    if self.user.Active:
        handleGetBuddies(self, data)
        handleGetBestFriends(self, data)
        handleGetPendingRequests(self, data)
        handleGetCharacters(self, data)

@Handlers.Handle(XT.GetPendingRequests)
def handleGetPendingRequests(self, data):
    pendingRequests = []

    if len(self.requests):
        for buddyId, buddyNickname in self.requests.items():
            pendingRequests.append("{}|{}".format(buddyId, buddyNickname))

        self.sendXt("pr", *pendingRequests)

@Handlers.Handle(XT.GetBuddies)
def handleGetBuddies(self, data):
    playerBuddies = []

    if len(self.buddies) > 0:
        for buddyId, buddyNickname in self.buddies.items():
            status = "online" if buddyId in self.server.players else "offline"
            playerBuddies.append("{}|{}|{}|{}".format(buddyId, buddyId, buddyNickname, status))

        self.sendXt("gb", *playerBuddies)

@Handlers.Handle(XT.GetBestFriends)
def handleGetBestFriends(self, data):
    if len(self.bestBuddies) > 0:
        bestFriendsString = "%".join("{}".format(buddyId) for buddyId in self.bestBuddies)

        self.sendXt("gbf", bestFriendsString)

@Handlers.Handle(XT.GetCharacters)
def handleGetCharacters(self, data):
    if len(self.characterBuddies) > 0:
        characterBuddiesString = "%".join("{}".format(characterId) for characterId in self.characterBuddies)

        self.sendXt("gc", characterBuddiesString)

@Handlers.Handle(XT.ToggleBestFriend)
def handleToggleBestFriend(self, data):
    if "character_" not in str(data.Id):

        if data.Id not in self.buddies:
            return self.transport.loseConnection()

        type = 1 if data.Id in self.bestBuddies else 2

        if type == 2:
            self.bestBuddies.append(data.Id)
        else:
            self.bestBuddies.remove(data.Id)

        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).update({"Type": type})

@Handlers.Handle(XT.BuddyRequest)
def handleBuddyRequest(self, data):
    if not self.user.Active:
        return self.transport.loseConnection()

    if "|" in data.Player:
        wantedBuddyId = int(data.Player.split("|")[1])
    else:
        wantedBuddyId = int(data.Player)

    if wantedBuddyId in self.server.mascots:
        return self.transport.loseConnection()

    if wantedBuddyId == self.user.ID:
        # Don't let people add themselves
        return self.transport.loseConnection()

    if wantedBuddyId not in self.buddies:
        request = BuddyList(PenguinID=wantedBuddyId, BuddyID=self.user.ID, Type=0)
        self.session.add(request)
        self.session.commit()

        if wantedBuddyId in self.server.players:
            player = self.server.players[wantedBuddyId]
            if player.user.Active:
                player.requests[self.user.ID] = self.user.Nickname
                player.sendXt("pr", "{}|{}".format(self.user.ID, self.user.Nickname))

@Handlers.Handle(XT.CharacterRequest)
def handleCharacterRequest(self, data):
    if data.Id in self.server.mascots:
        if not self.user.Active:
            return self.transport.loseConnection()

        mascotStampId = self.session.query(Penguin.MascotStamp).filter(Penguin.ID == data.Id).first()

        if mascotStampId[0] != 0:
            if data.Id not in self.server.players and mascotStampId[0] not in self.stamps:
                # Prevent hackers from force-adding characters
                # Note that this won't work for characters without stamps
                return cheatBan(self, self.user.ID, 72, "Attempting to force-add a character to friends list")

        if data.Id not in self.characterBuddies:
            self.characterBuddies.append(data.Id)

            request = BuddyList(PenguinID=self.user.ID, BuddyID=data.Id, Type=3)
            self.session.add(request)

            self.sendXt("cr", data.Id)

@Handlers.Throttle(1)
@Handlers.Handle(XT.BuddyAccept)
def handleBuddyAccept(self, data):
    if data.Id in self.server.mascots:
        return self.transport.loseConnection()

    if not self.user.Active:
        return self.transport.loseConnection()

    if data.Id == self.user.ID:
        return self.transport.loseConnection()

    if data.Id not in self.requests:
        # Prevent hackers from adding players that haven't sent requests
        return cheatBan(self, self.user.ID, 72, "Attempting to add player to friends list")

    doubleRequest = self.session.query(BuddyList.BuddyID,Penguin.Nickname).join(Penguin, Penguin.ID == BuddyList.BuddyID). \
            filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID,BuddyList.Type == 0)).first()

    # Check if the players have both sent each other a request
    if doubleRequest:
        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID,BuddyList.Type == 0)).update({"Type": 1})
    else:
        accept = BuddyList(PenguinID=data.Id, BuddyID=self.user.ID, Type=1)
        self.session.add(accept)

    del self.requests[data.Id]
    data.Nickname = getPlayerInfo(self, data.Id).split("|")[0]
    self.buddies[data.Id] = data.Nickname

    self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).update({"Type": 1})
    self.session.commit()

    status = "online" if data.Id in self.server.players else "offline"
    newBuddy = "{}|{}|{}|{}".format(data.Id, data.Id, data.Nickname, status)

    self.sendXt("ba", newBuddy)
    handleRefreshPlayerFriendInfo(self, data)

    if data.Id in self.server.players:
        player = self.server.players[data.Id]
        player.sendXt("ba", "{}|{}|{}|online".format(self.user.ID, self.user.ID, self.user.Nickname))
        player.buddies[self.user.ID] = self.user.Nickname
        handleRefreshPlayerFriendInfo(player, data)

@Handlers.Handle(XT.BuddyReject)
def handleBuddyReject(self, data):
    if data.Id in self.requests:
        del self.requests[data.Id]
        self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id,BuddyList.Type == 0)).delete()

        self.sendXt("rr", data.Id)

@Handlers.Handle(XT.RemoveBuddy)
def handleRemoveBuddy(self, data):
    if data.Id not in self.server.mascots:
        if data.Id in self.buddies:
            del self.buddies[data.Id]
            if data.Id in self.bestBuddies: self.bestBuddies.remove(data.Id)

            self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == self.user.ID,BuddyList.BuddyID == data.Id)).delete()
            self.session.query(BuddyList).filter(and_(BuddyList.PenguinID == data.Id,BuddyList.BuddyID == self.user.ID)).delete()

            self.session.commit()

            self.sendXt("rb", data.Id)
            handleRefreshPlayerFriendInfo(self, data)

            if data.Id in self.server.players:
                player = self.server.players[data.Id]
                player.sendXt("rb", self.user.ID)
                del player.buddies[self.user.ID]
                if self.user.ID in player.bestBuddies: player.bestBuddies.remove(self.user.ID)
                handleRefreshPlayerFriendInfo(player, data)

@Handlers.Handle(XT.GetBestFriendsIglooList)
def handleGetBestFriendsIglooList(self, data):
    self.sendXt("gbffl", ",".join("{}".format(buddyId) for buddyId in self.bestBuddies))

@Handlers.Handle(XT.GetFriendsIglooList)
def GetFriendsIglooList(self, data):
    buddyIgloos = []

    for buddyId in self.buddies.keys():
        likes = getActiveIgloo(self, buddyId).split(":")[8]
        buddyIgloos.append("{}|{}".format(buddyId, likes))

    self.sendXt("grf", *buddyIgloos)

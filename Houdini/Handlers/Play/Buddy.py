from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, BuddyList

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


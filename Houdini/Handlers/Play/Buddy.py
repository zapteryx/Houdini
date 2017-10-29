from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.GetBuddyList)
def handleGetBuddyList(self, data):
    buddiesArray = []

    for buddyId, buddyName in self.buddies.items():
        buddiesArray.append("%d|%s|%d" % (buddyId, buddyName,
                              1 if buddyId in self.server.players else 0))

    self.sendXt("gb", "%".join(buddiesArray))

# TODO check if the user is ignored
@Handlers.Handle(XT.BuddyRequest)
def handleBuddyRequest(self, data):
    # Maybe use the or keyword?
    if len(self.buddies) >= 100:
        return

    if data.Id in self.buddies:
        return

    if data.Id not in self.server.players:
        return

    buddyObject = self.server.players[data.Id]

    if not hasattr(buddyObject, "buddyRequests"):
        buddyObject.buddyRequests = {}

    buddyObject.buddyRequests[self.user.ID] = [self.user.Username, self.buddies]

    buddyObject.sendXt("br", self.user.ID, self.user.Username)


@Handlers.Handle(XT.BuddyAccept)
def handleBuddyAccept(self, data):
    if data.Id not in self.buddyRequests:
        return

    buddyUsername, buddyBuddies = self.buddyRequests[data.Id]
    self.buddies[data.Id] = buddyUsername

    buddyString = "%".join(["%s|%s" % (buddyId, buddyUsername) for (buddyId, buddyUsername) in self.buddies.items()])
    self.user.Buddies = buddyString

    buddyBuddies[self.user.ID] = self.user.Username
    buddyString = "%".join(["%s|%s" % (buddyId, buddyUsername) for (buddyId, buddyUsername) in buddyBuddies.items()])
    self.logger.debug("buddyBuddies string: %s", buddyString)

    self.session.query(Penguin).\
        filter(Penguin.ID == data.Id).\
        update({"Buddies": buddyString})

    self.session.commit()

    del self.buddyRequests[data.Id]

    try:
        buddyObject = self.server.players[data.Id]

        buddyObject.sendXt("ba", self.user.ID, self.user.Username)
        buddyObject.buddies = buddyBuddies

    except KeyError:
        self.sendXt("bof", data.Id)

    finally:
        self.logger.debug("%d and %d are now buddies.", data.Id, self.user.ID)


@Handlers.Handle(XT.RemoveBuddy)
def handleRemoveBuddy(self, data):
    if data.Id not in self.buddies:
        return

    del self.buddies[data.Id]

    buddyString = "%".join(["%s|%s" % (buddyId, buddyUsername) for (buddyId, buddyUsername) in self.buddies.items()])
    self.user.Buddies = buddyString

    self.session.query(Penguin). \
        filter(Penguin.ID == self.user.ID). \
        update({"Buddies": buddyString})

    buddy = self.session.query(Penguin).filter_by(ID=data.Id).first()
    oldBuddiesArray = buddy.Buddies.split("%")
    newBuddiesArray = []

    for buddyPair in oldBuddiesArray:
        buddyId, buddyUsername = buddyPair.split("|")

        if self.user.ID != int(buddyId):
            newBuddiesArray.append(buddyPair)

    buddyString = "%".join(newBuddiesArray)
    buddy.Buddies = buddyString

    self.session.commit()

    try:
        buddyObject = self.server.players[data.Id]

        buddyObject.sendXt("rb", self.user.ID)
        del buddyObject.buddies[self.user.ID]

    except KeyError:
        self.logger.debug("%d tried removing an offline buddy (%d)", self.user.ID, data.Id)

    finally:
        self.logger.debug("%d and %d are no longer buddies", self.user.ID, data.Id)


# Possible TODO: Check if data.Id is a buddy?
@Handlers.Handle(XT.FindBuddy)
def handleFindBuddy(self, data):
    try:
        buddyObject = self.server.players[data.Id]
        self.sendXt("bf", buddyObject.room.Id)

    except KeyError:
        self.logger.debug("%s (%d) tried to find a buddy who was offline!", self.user.Username, self.user.ID)
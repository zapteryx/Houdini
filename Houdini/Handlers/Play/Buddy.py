from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, BuddyList

@Handlers.Handle(XT.GetBuddyList)
@Handlers.Throttle(-1)
def handleGetBuddyList(self, data):
    buddiesArray = []

    for buddyId, buddyName in self.buddies.items():
        buddiesArray.append("%d|%s|%d" % (buddyId, buddyName,
                              1 if buddyId in self.server.players else 0))

    self.sendXt("gb", "%".join(buddiesArray))

@Handlers.Handle(XT.BuddyRequest)
def handleBuddyRequest(self, data):
    if len(self.buddies) >= 100:
        return

    if data.Id in self.buddies:
        return

    if data.Id not in self.server.players:
        return

    buddyObject = self.server.players[data.Id]

    if self.user.ID in buddyObject.ignore:
        return

    if not hasattr(buddyObject, "buddyRequests"):
        buddyObject.buddyRequests = {}
    elif self.user.ID in buddyObject.buddyRequests:
        return

    buddyObject.buddyRequests[self.user.ID] = [self.user.Username, self.buddies]

    buddyObject.sendXt("br", self.user.ID, self.user.Username)


@Handlers.Handle(XT.BuddyAccept)
def handleBuddyAccept(self, data):
    if data.Id not in self.buddyRequests:
        return

    buddyUsername, buddyBuddies = self.buddyRequests[data.Id]
    self.buddies[data.Id] = buddyUsername

    buddyBuddies[self.user.ID] = self.user.Username

    self.engine.execute(BuddyList.insert(),
                        { "PenguinID": self.user.ID, "BuddyID": data.Id },
                        { "PenguinID": data.Id, "BuddyID": self.user.ID })

    del self.buddyRequests[data.Id]

    try:
        buddyObject = self.server.players[data.Id]
        buddyObject.sendXt("ba", self.user.ID, self.user.Username)
    except KeyError:
        self.sendXt("bof", data.Id)
    finally:
        self.logger.debug("%d and %d are now buddies.", data.Id, self.user.ID)


@Handlers.Handle(XT.RemoveBuddy)
def handleRemoveBuddy(self, data):
    if data.Id not in self.buddies:
        return

    del self.buddies[data.Id]

    self.engine.execute(BuddyList.delete().where(
        ((BuddyList.c.PenguinID == self.user.ID) & (BuddyList.c.BuddyID == data.Id)) |
        ((BuddyList.c.PenguinID == data.Id) & (BuddyList.c.BuddyID == self.user.ID))))

    try:
        buddyObject = self.server.players[data.Id]

        buddyObject.sendXt("rb", self.user.ID)
        del buddyObject.buddies[self.user.ID]
    except KeyError:
        self.logger.debug("%d tried removing an offline buddy (%d)", self.user.ID, data.Id)

    finally:
        self.logger.debug("%d and %d are no longer buddies", self.user.ID, data.Id)


@Handlers.Handle(XT.FindBuddy)
def handleFindBuddy(self, data):
    try:
        if data.Id not in self.buddies:
            return

        buddyObject = self.server.players[data.Id]
        self.sendXt("bf", buddyObject.room.Id)
    except KeyError:
        self.logger.debug("%s (%d) tried to find a buddy who was offline!", self.user.Username, self.user.ID)
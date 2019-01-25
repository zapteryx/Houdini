import threading

from Houdini.Handlers import Handlers, XT
from Houdini.Events import Events
from Houdini.Handlers.Play.Pet import handleSendPuffleWalk

@Handlers.Handle(XT.PlayerTransformation)
def handlePlayerTransformation(self, data):
    if data.TransformationId != 0 and data.TransformationId not in self.server.availableTransformations.keys():
        return

    if hasattr(self, 'transformationTimer'):
        self.transformationTimer.cancel()

    if data.TransformationId == 0:
        handleRevertPlayerTransformation(self, data)

    membersOnly = self.server.availableTransformations[data.TransformationId][0]
    duration = self.server.availableTransformations[data.TransformationId][1]

    if membersOnly == 1 and self.user.Member == 0:
        return

    self.user.Avatar = data.TransformationId

    if duration != 0 and self.user.Moderator == 0:
        self.transformationTimer = threading.Timer(duration, handleRevertPlayerTransformation, [self, data])
        self.transformationTimer.start()

    if self.walkingPuffle:
        data.PuffleId = self.walkingPuffle.ID 
        handleSendPuffleWalk(self, data)

    if self.user.Moderator != 2:
        self.room.sendXt("spts", self.user.ID, data.TransformationId)
    else:
        self.sendXt("spts", self.user.ID, data.TransformationId)

def handleRevertPlayerTransformation(self, data):
    if self.user.Moderator != 2:
        return self.room.sendXt("spts", self.user.ID, 0)
    else:
        return self.sendXt("spts", self.user.ID, 0)

def handleDisconnection(self):
    if self.server.server["World"]:
        if hasattr(self, 'transformationTimer'):
            self.transformationTimer.cancel()

        if self.user.Moderator == 0:
            self.user.Avatar = 0

Events.Register("Disconnected", handleDisconnection)

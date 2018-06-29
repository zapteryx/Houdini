from datetime import datetime, timedelta

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Ban import Ban

from sqlalchemy.sql import select, func

from twisted.internet.defer import inlineCallbacks

@Handlers.Handle(XT.BanPlayer)
def handleBanPlayer(self, data):
    if self.user.Moderator:
        moderatorBan(self, data.PlayerId, comment=data.Message)

@Handlers.Handle(XT.MutePlayer)
def handleMutePlayer(self, data):
    if self.user.Moderator:
        if data.PlayerId in self.server.players:
            target = self.server.players[data.PlayerId]
            if not target.user.Moderator:
                target.muted = True

@Handlers.Handle(XT.KickPlayer)
def handleKickPlayer(self, data):
    if self.user.Moderator:
        moderatorKick(self, data.PlayerId)

def cheatKick(self, targetPlayer):
    if targetPlayer in self.server.players:
        self.server.players[targetPlayer].sendErrorAndDisconnect(800)

@inlineCallbacks
def cheatBan(self, targetPlayer, banDuration=24, comment=""):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        result = yield self.engine.execute(select([func.count()]).select_from(
            Ban).where(Ban.c.PenguinID == targetPlayer))
        numberOfBans = yield result.scalar()

        dateIssued = datetime.now()
        dateExpires = dateIssued + timedelta(hours=banDuration)
        self.engine.execute(Ban.insert(), PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                  ModeratorID=None, Reason=1, Comment=comment)
        if numberOfBans >= 3:
            target.user.Permaban = True

        target.sendXt("e", 611, comment)
        target.transport.loseConnection()

def moderatorKick(self, targetPlayer):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if not target.user.Moderator:
            for (playerId, player) in self.server.players.items():
                if player.user.Moderator:
                    player.sendXt("ma", "k", targetPlayer, target.user.Username)
            target.sendErrorAndDisconnect(5)

@inlineCallbacks
def moderatorBan(self, targetPlayer, banDuration=24, comment=""):
    target = yield self.engine.first(Penguin.select(Penguin.c.ID == targetPlayer))

    if not target.Moderator:
        for (playerId, player) in self.server.players.items():
            if player.user.Moderator:
                player.sendXt("ma", "b", targetPlayer, target.Username)

        result = yield self.engine.execute(select([func.count()]).select_from(
            Ban).where(Ban.c.PenguinID == targetPlayer))
        numberOfBans = yield result.scalar()

        dateIssued = datetime.now()
        dateExpires = dateIssued + timedelta(hours=banDuration)
        self.engine.execute(Ban.insert(), PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                  ModeratorID=self.user.ID, Reason=2, Comment=comment)
        if numberOfBans >= 3:
            target.Permaban = True

        if targetPlayer in self.server.players:
            self.server.players[targetPlayer].sendXt("e", 610, comment)
            self.server.players[targetPlayer].transport.loseConnection()
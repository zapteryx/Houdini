from datetime import datetime, timedelta

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Ban import Ban

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

def cheatBan(self, targetPlayer, banDuration=72, comment=""):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        numberOfBans = self.session.query(Ban).\
            filter(Ban.PenguinID == targetPlayer).filter(Ban.Reason == 1).count()

        dateIssued = datetime.now()
        dateExpires = dateIssued + timedelta(hours=banDuration)
        if numberOfBans < 1:
            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=None, Reason=1, Comment=comment)
        else:
            target.user.Permaban = True
            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=None, Reason=1, Comment=comment)

        self.session.add(ban)

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

def moderatorBan(self, targetPlayer, banDuration=24, comment=""):
    target = self.session.query(Penguin).\
        filter_by(ID=targetPlayer).first()

    if not target.Moderator:
        for (playerId, player) in self.server.players.items():
            if player.user.Moderator:
                player.sendXt("ma", "b", targetPlayer, target.Username)

        numberOfBans = self.session.query(Ban).\
            filter(Ban.PenguinID == targetPlayer).count()

        dateIssued = datetime.now()
        dateExpires = dateIssued + timedelta(hours=banDuration)
        if numberOfBans < 3:
            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=self.user.ID, Reason=2, Comment=comment)
        else:
            target.Permaban = True
            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=self.user.ID, Reason=2, Comment=comment)

        self.session.add(ban)

        if targetPlayer in self.server.players:
            self.server.players[targetPlayer].sendXt("e", 610, comment)
            self.server.players[targetPlayer].transport.loseConnection()
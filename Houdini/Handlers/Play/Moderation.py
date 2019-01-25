from datetime import datetime, timedelta

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Ban import Ban
from Houdini.Data.PlayerReport import PlayerReport
from Houdini.Data.Warnings import Warnings

@Handlers.Handle(XT.BanPlayer)
def handleBanPlayer(self, data):
    if self.user.Moderator != 0:
        moderatorBan(self, data.PlayerId, comment=data.Message)

@Handlers.Handle(XT.MutePlayer)
def handleMutePlayer(self, data):
    if self.user.Moderator != 0:
        if data.PlayerId in self.server.players:
            target = self.server.players[data.PlayerId]
            if target.user.Moderator == 0:
                target.muted = True

@Handlers.Handle(XT.KickPlayer)
def handleKickPlayer(self, data):
    if self.user.Moderator != 0:
        moderatorKick(self, data.PlayerId)

@Handlers.Handle(XT.ReportPlayer)
@Handlers.Throttle(5)
def handleReportPlayer(self, data):
    reportee = data.Report[0]
    if len(data.Report) > 1:
        reason = data.Report[1]
    else:
        reason = None
    timestamp = datetime.now()
    serverId = self.server.server["Id"]

    report = PlayerReport(PenguinID=reportee, ReporterID=self.user.ID, Reason=reason,
                Timestamp=timestamp, ServerID=serverId, RoomID=self.room.Id)
    self.session.add(report)
    self.session.commit()

def cheatBan(self, targetPlayer, banDuration=72, comment=""):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfCheatingBans = self.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).filter(Ban.Reason == 1).count()

            numberOfBans = self.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfCheatingBans >= 1 or numberOfBans >= 3:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                    ModeratorID=None, Reason=1, Comment=comment)
            self.session.add(ban)

            target.sendXt("ban", "611", targetPlayer, banDuration)
            target.transport.loseConnection()

def languageWarn(self, targetPlayer):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(days=7)

            warn = Warnings(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                          Type=1)

            target.session.add(warn)
            target.session.commit()

            target.sendXt("moderatormessage", "2", targetPlayer)

def languageBan(self, targetPlayer, banDuration=24, comment="Bad language"):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfActiveLanguageWarns = target.session.query(Warnings).\
                filter(Warnings.PenguinID == targetPlayer).filter(Warnings.Type == 1).filter(Warnings.Expires >= datetime.now()).count()

            if numberOfActiveLanguageWarns == 0:
                return languageWarn(self, targetPlayer)

            numberOfBans = target.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfBans >= 3:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=None, Reason=3, Comment=comment)
            target.session.add(ban)

            target.sendXt("ban", "610", None, banDuration, targetPlayer)
            target.transport.loseConnection()

def moderatorKick(self, targetPlayer):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            target.sendXt("moderatormessage", "3", targetPlayer)
            target.transport.loseConnection()

def moderatorBan(self, targetPlayer, banDuration=24, comment=""):
    target = self.session.query(Penguin).\
        filter_by(ID=targetPlayer).first()

    if target.Moderator == 0:
        numberOfBans = self.session.query(Ban).\
            filter(Ban.PenguinID == targetPlayer).count()

        dateIssued = datetime.now()
        dateExpires = dateIssued + timedelta(hours=banDuration)

        if numberOfBans >= 3 or banDuration == 0:
            target.Permaban = True
            banDuration = 0

        ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                  ModeratorID=self.user.ID, Reason=2, Comment=comment)
        self.session.add(ban)

        if targetPlayer in self.server.players:
            self.server.players[targetPlayer].sendXt("ban", "612", None, banDuration, targetPlayer)
            self.server.players[targetPlayer].transport.loseConnection()

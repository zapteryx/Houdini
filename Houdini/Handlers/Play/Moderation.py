from datetime import datetime, timedelta

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Ban import Ban
from Houdini.Data.PlayerReport import PlayerReport
from Houdini.Data.Warnings import Warnings

@Handlers.Handle(XT.BanPlayer)
def handleBanPlayer(self, data):
    if self.user.Moderator != 0:
        targetPlayer = data.PlayerId
        data.Comment = None if data.Comment == " " else data.Comment
        if data.Reason == 4:
            return cheatBan(self, targetPlayer, data.Duration, data.Comment, self.user.ID)
        if data.Reason == 8:
            return languageBan(self, targetPlayer, data.Duration, data.Comment, self.user.ID)
        if data.Reason == 6:
            return bullyingBan(self, targetPlayer, data.Duration, data.Comment, self.user.ID)
        if data.Reason == 7:
            return personalInfoBan(self, targetPlayer, data.Duration, data.Comment, self.user.ID)

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

@Handlers.Handle(XT.InitBan)
def handleInitBan(self, data):
    if self.user.Moderator != 0:
        targetPlayer = data.PlayerId
        if targetPlayer in self.server.players:
            target = self.server.players[targetPlayer]

            if target.user.Moderator == 0:
                numberOfBans = self.session.query(Ban).\
                    filter(Ban.PenguinID == targetPlayer).count()

                self.sendXt("initban", targetPlayer, 0, numberOfBans, data.Phrase, target.user.Nickname)

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

def cheatBan(self, targetPlayer, banDuration=72, comment=None, moderatorId=None):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfCheatingBans = self.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).filter(Ban.Reason == 4).count()

            numberOfBans = self.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfCheatingBans >= 1 or numberOfBans >= 3 or banDuration == 0:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                    ModeratorID=moderatorId, Reason=4, Comment=comment)
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

            target.sendXt("moderatormessage", 2)

def languageBan(self, targetPlayer, banDuration=24, comment=None, moderatorId=None):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfActiveLanguageWarns = target.session.query(Warnings).\
                filter(Warnings.PenguinID == targetPlayer).filter(Warnings.Type == 1).filter(Warnings.Expires >= datetime.now()).count()

            if numberOfActiveLanguageWarns == 0 and moderatorId is None:
                return languageWarn(self, targetPlayer)

            numberOfBans = target.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfBans >= 3 or banDuration == 0:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=moderatorId, Reason=1, Comment=comment)
            target.session.add(ban)

            target.sendXt("ban", "610", None, banDuration, targetPlayer)
            target.transport.loseConnection()

def personalInfoBan(self, targetPlayer, banDuration=24, comment=None, moderatorId=None):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfBans = target.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfBans >= 3 or banDuration == 0:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=moderatorId, Reason=3, Comment=comment)
            target.session.add(ban)

            target.sendXt("ban", "612", 7, banDuration, targetPlayer)
            target.transport.loseConnection()

def bullyingBan(self, targetPlayer, banDuration=24, comment=None, moderatorId=None):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            numberOfBans = target.session.query(Ban).\
                filter(Ban.PenguinID == targetPlayer).count()

            if numberOfBans >= 3 or banDuration == 0:
                banDuration = 0
                target.user.Permaban = True

            dateIssued = datetime.now()
            dateExpires = dateIssued + timedelta(hours=banDuration)

            ban = Ban(PenguinID=targetPlayer, Issued=dateIssued, Expires=dateExpires,
                      ModeratorID=moderatorId, Reason=2, Comment=comment)
            target.session.add(ban)

            target.sendXt("ban", "612", 6, banDuration, targetPlayer)
            target.transport.loseConnection()

def moderatorKick(self, targetPlayer):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        if target.user.Moderator == 0:
            target.sendXt("moderatormessage", 3)
            target.transport.loseConnection()

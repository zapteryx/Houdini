from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.Ban import Ban
import time

@Handlers.Handle(XT.BanPlayer)
def handleBanPlayer(self, data):
    if self.user.Moderator:
        moderatorBan(self, data.PlayerId, comment=data.Message)

@Handlers.Handle(XT.MutePlayer)
def handleMutePlayer(self, data):
    return

@Handlers.Handle(XT.KickPlayer)
def handleKickPlayer(self, data):
    if self.user.Moderator:
        moderatorKick(self, data.PlayerId)

def cheatKick(self, targetPlayer):
    if targetPlayer in self.server.players:
        self.server.players[targetPlayer].sendErrorAndDisconnect(800)

def cheatBan(self, targetPlayer, banDuration=24, comment=""):
    if targetPlayer in self.server.players:
        target = self.server.players[targetPlayer]
        numberOfBans = self.session.query(Ban).\
            filter(Ban.Player == targetPlayer).\
            count()

        if numberOfBans < 3:
            target.user.Banned = int(time.time() + 60 * 60 * banDuration)
            ban = Ban(Moderator="sys", Player=targetPlayer,
                      Comment=comment, Expiration=banDuration, Time=time.time())
        else:
            target.user.Banned = "perm"
            ban = Ban(Moderator="sys", Player=targetPlayer,
                      Comment=comment, Expiration="perm", Time=time.time())

        self.session.add(ban)
        self.session.commit()

        target.sendXt("e", 611, comment)

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
            filter(Ban.Player == targetPlayer).\
            count()

        if numberOfBans < 3:
            target.Banned = int(time.time() + 60 * 60 * banDuration)
            ban = Ban(Moderator=self.user.Username, Player=targetPlayer,
                      Comment=comment, Expiration=banDuration, Time=time.time())
        else:
            target.Banned = "perm"
            ban = Ban(Moderator=self.user.Username, Player=targetPlayer,
                      Comment=comment, Expiration="perm", Time=time.time())

        self.session.add(ban)
        self.session.commit()

        if targetPlayer in self.server.players:
            self.server.players[targetPlayer].sendXt("e", 610, comment)
            self.server.players[targetPlayer].transport.loseConnection()
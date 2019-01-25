from beaker.cache import cache_region as Cache
from sqlalchemy import or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, NameApproval
from Houdini.Data.Membership import Membership
from Houdini.Data.Puffle import Puffle

@Cache("houdini", "player")
def getPlayerString(self, penguinId):
    if penguinId in self.server.players:
        player = self.server.players[penguinId]
        playerTuple = (player.user.ID, player.user.Nickname, player.user.Approval, player.user.Color, player.user.Head,
                       player.user.Face, player.user.Neck, player.user.Body, player.user.Hand,
                       player.user.Feet, player.user.Flag, player.user.Photo, player.user.Member, player.user.MembershipDays)
        playerData = "{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}|{11}||||{12}|{13}"
        playerData = playerData.format(*playerTuple)

        puffleTuple = (player.walkingPuffle.ID, player.walkingPuffle.Type, player.walkingPuffle.Subtype, player.walkingPuffle.Hat) if player.walkingPuffle else None
    else:
        playerTuple = self.session.query(Penguin.ID, Penguin.Nickname, Penguin.Color, Penguin.Head,
                                         Penguin.Face, Penguin.Neck, Penguin.Body, Penguin.Hand, Penguin.Feet, Penguin.Flag,
                                         Penguin.Photo).filter_by(ID=penguinId).first()
        approvalTuple = self.session.query(NameApproval.en).filter_by(PenguinID=penguinId).first()
        membershipTuple = self.session.query(Membership.Status, Membership.CumulativeDays).filter_by(PenguinID=penguinId).first()
        playerData = "{0}|{1}|nameApproval|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}||||membership|memberDays"
        playerData = playerData.format(*playerTuple)
        nameApproval = "1" if approvalTuple[0] == 1 else "0"
        playerData = playerData.replace("nameApproval", nameApproval)
        playerData = playerData.replace("membership", str(membershipTuple[0]))
        playerData = playerData.replace("memberDays", str(membershipTuple[1]))

        puffleTuple = self.session.query(Puffle.ID, Puffle.Type, Puffle.Subtype, Puffle.Hat).filter_by(PenguinID=penguinId).filter_by(Walking=1).first()

    if playerTuple is not None:
        if puffleTuple is not None:
            playerData += "||||{0}|{1}|{2}|{3}|0"
            playerData = playerData.format(*puffleTuple)

        return playerData

    return str()

@Cache("houdini", "player_info")
def getPlayerInfo(self, penguinId):
    if penguinId in self.server.players:
        player = self.server.players[penguinId]
        playerTuple = (player.user.Nickname, player.user.ID, player.user.Nickname)
    else:
        playerTuple = self.session.query(Penguin.Nickname, Penguin.ID, Penguin.Nickname).filter_by(ID=penguinId).first()

    if playerTuple is not None:
        playerData = [str(playerDetail) for playerDetail in playerTuple]
        return "|".join(playerData)

    return str()

@Handlers.Handle(XT.Heartbeat)
@Handlers.Throttle(60)
def handleSendHeartbeat(self, data):
    self.sendXt("h")

@Handlers.Handle(XT.ThrowBall)
@Handlers.Throttle()
def handlePlayerThrowBall(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("sb", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerMove)
def handleSendPlayerMove(self, data):
    if self.user.Moderator != 2:
        self.x = data.X
        self.y = data.Y

        self.room.sendXt("sp", self.user.ID, data.X, data.Y)

@Handlers.Handle(XT.PlayerAction)
@Handlers.Throttle()
def handleUpdatePlayerAction(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("sa", self.user.ID, data.Id)

@Handlers.Handle(XT.SendEmote)
@Handlers.Throttle()
def handleSendEmote(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("se", self.user.ID, data.Id)

@Handlers.Handle(XT.PlayerFrame)
@Handlers.Throttle()
def handleSendPlayerFrame(self, data):
    if self.user.Moderator != 2:
        self.frame = data.Id
        self.room.sendXt("sf", self.user.ID, data.Id)

@Handlers.Handle(XT.SendJoke)
@Handlers.Throttle()
def handleSendJoke(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("sj", self.user.ID, data.Id)

@Handlers.Handle(XT.SendSafe)
@Handlers.Throttle()
def handleSafeMessage(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("ss", self.user.ID, data.Id)

@Handlers.Handle(XT.SendTourGuide)
@Handlers.Throttle()
def handleSendTourGuide(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("sg", self.user.ID, data.Id)

@Handlers.Handle(XT.SendLineMessage)
@Handlers.Throttle()
def handleSendLineMessage(self, data):
    if self.user.Moderator != 2:
        self.room.sendXt("sl", self.user.ID, data.Id)

@Handlers.Handle(XT.SendMascotMessage)
@Handlers.Throttle()
def handleSendMascotMessage(self, data):
    if self.user.MascotStamp:
        self.room.sendXt("sma", self.user.ID, data.Id)

@Handlers.Handle(XT.GetLatestRevision)
@Handlers.Throttle(-1)
def handleGetLatestRevision(self, data):
    self.room.sendXt("glr", "0")

@Handlers.Handle(XT.GetPlayer)
@Handlers.Throttle()
def handleLoadPlayerObject(self, data):
    self.sendXt("gp", getPlayerString(self, data.Id))

@Handlers.Handle(XT.GetCharacter)
@Handlers.Throttle()
def handleLoadMascotObject(self, data):
    self.sendXt("gmo", getPlayerString(self, data.Id))

@Handlers.Handle(XT.GetPlayerInfoById)
@Handlers.Throttle()
def handleGetPlayerInfoById(self, data):
    self.sendXt("pbi", getPlayerInfo(self, data.Id))

@Handlers.Handle(XT.GetPlayerInfoByName)
@Handlers.Throttle()
def handleGetPlayerInfoByName(self, data):
    playerArray = self.session.query(Penguin.ID).filter_by(Nickname=data.Name).first()

    if playerArray:
        playerId = playerArray[0]
        self.sendXt("pbn", playerId, playerId, data.Name)
    else:
        self.sendXt("pbn")

@Handlers.Handle(XT.GetPlayerInfoBySwid)
@Handlers.Throttle()
def handleGetPlayerInfoBySwid(self, data):
    playerInfo = getPlayerInfo(self, data.Id)
    nickname = playerInfo.split("|")[2]
    self.sendXt("pbs", data.Id, data.Id, nickname)

@Handlers.Handle(XT.PlayerBySwidUsername)
@Handlers.Throttle()
def handlePlayerBySwidUsername(self, data):
    playerIds = data.IdList.split(",")

    nicknames = self.session.query(Penguin.Nickname)\
        .filter(or_(*((Penguin.ID == playerId) for playerId in playerIds))).all()

    self.sendXt("pbsu", ",".join([nickname for nickname, in nicknames]))


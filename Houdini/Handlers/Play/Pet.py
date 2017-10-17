import time, random

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Puffle import Puffle

@Handlers.Handle(XT.GetPlayerPuffles)
def handleGetPuffles(self, data):
    ownedPuffles = ownedPuffles = self.session.query(Puffle).filter(Puffle.Owner == data.PlayerId)

    playerPuffles = ["%d|%s|%d|%d|%d|%d|100|100|100|0|0|%d" % (puffle.ID, puffle.Name, puffle.Type, puffle.Health,
                                                               puffle.Hunger, puffle.Rest, puffle.Walking)
                     for puffle in ownedPuffles]

    playerPufflesString = "%".join(playerPuffles)

    self.sendXt("pg", playerPufflesString)

@Handlers.Handle(XT.GetMyPlayerPuffles)
def handleGetMyPlayerPuffles(self, data):
    ownedPuffles = self.session.query(Puffle).filter(Puffle.Owner == self.user.ID)

    for ownedPuffle in ownedPuffles:
        self.puffles[ownedPuffle.ID] = ownedPuffle

    playerPuffles = ["%d|%s|%d|%d|%d|%d|100|100|100" % (puffle.ID, puffle.Name, puffle.Type, puffle.Health,
                                                        puffle.Hunger, puffle.Rest)
                     for puffle in ownedPuffles]

    myPufflesString = "%".join(playerPuffles)

    self.sendXt("pgu", myPufflesString)

@Handlers.Handle(XT.AdoptPuffle)
def handleSendAdoptPuffle(self, data):
    if self.user.Coins < 800:
        return self.sendError(401)

    self.user.Coins -= 800

    puffle = Puffle(Owner=self.user.ID, Name=data.Name, AdoptionDate=time.time(), Type=data.TypeId)
    self.session.add(puffle)
    self.session.commit()

    puffleString = "%d|%s|%d|100|100|100|100|100|100" % (puffle.ID, data.Name, data.TypeId)
    self.sendXt("pn", self.user.Coins, puffleString)

    """
    The code below is a copy of handleGetMyPlayerPuffles.
    Might want to make a reusable function for this later?
    """
    ownedPuffles = self.session.query(Puffle).filter(Puffle.Owner == self.user.ID)

    for ownedPuffle in ownedPuffles:
        self.puffles[ownedPuffle.ID] = ownedPuffle

    playerPuffles = ["%d|%s|%d|%d|%d|%d|100|100|100" % (puffle.ID, puffle.Name, puffle.Type, puffle.Health,
                                                        puffle.Hunger, puffle.Rest)
                     for puffle in ownedPuffles]

    myPufflesString = "%".join(playerPuffles)

    self.sendXt("pgu", myPufflesString)

@Handlers.Handle(XT.MovePuffle)
def handleSendPuffleMove(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("pm", data.PuffleId, data.X, data.Y)

@Handlers.Handle(XT.WalkPuffle)
def handleSendPuffleWalk(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]
        if puffle.Rest < 20 and puffle.Hunger < 40:
            return # Client shouldn't have been allowed to send this packet

        puffle.Walking = 1 if not puffle.Walking else 0

        self.session.add(puffle)
        self.session.commit()

        # Blame Club Penguin and not me!
        puffleData = [data.PuffleId]
        puffleData[1:11] = [''] * 11
        puffleData.append(puffle.Walking)

        puffleString = "|".join([str(puffleElement) for puffleElement in puffleData])

        self.room.sendXt("pw", self.user.ID, puffleString)

@Handlers.Handle(XT.PlayPuffle)
def handleSendPufflePlay(self, data):
    if data.PuffleId in self.puffles:
        puffle = self.puffles[data.PuffleId]

        if puffle.Rest < 20 or puffle.Health < 10:
            return  # Client shouldn't have been allowed to send this packet

        additionalPlay = random.randrange(30, 55)
        negativeHunger = random.randrange(30, 40)
        negativeRest = random.randrange(30, 45)

        puffle.Health = max(30, min(puffle.Health + additionalPlay, 100))
        puffle.Hunger = max(0, min(puffle.Hunger - negativeHunger, 100))
        puffle.Rest = max(0, min(puffle.Rest - negativeRest, 100))

        playType = 1 if puffle.Rest > 80 else random.choice([1, 2])

        playString = "%d|Hou|dini|%d|%d|%d" % (puffle.ID, puffle.Health, puffle.Hunger, puffle.Rest)

        self.room.sendXt("pp", playString, playType)

@Handlers.Handle(XT.PuffleFrame)
def handleSendPuffleFrame(self, data):
    if data.PuffleId in self.puffles:
        self.room.sendXt("ps", data.PuffleId, data.FrameId)
import random, time
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Puffle import Puffle

def getPuffles(session, playerId):
    puffles = session.query(Puffle).filter(Puffle.Owner == playerId)

    # Some different ways to do this
    playerPuffles = ["%d|%s|%d|%d|%d|%d|%d" % (puffle.ID, puffle.Name, puffle.Type, puffle.Food,
                                               puffle.Play, puffle.Rest, puffle.Walking)
                     for puffle in puffles if not puffle.Walking]

    playerPufflesString = "%".join(playerPuffles)

    return playerPufflesString

@Handlers.Handle(XT.GetPlayerPuffles)
def handleGetPuffles(self, data):
    pufflesString = getPuffles(self.session, self.user.ID)
    self.sendXt("pg", pufflesString)

@Handlers.Handle(XT.GetMyPlayerPuffles)
def handleGetMyPlayerPuffles(self, data):
    pufflesString = getPuffles(self.session, self.user.ID)
    self.sendXt("pgu", pufflesString)

@Handlers.Handle(XT.AdoptPuffle)
def handleSendAdoptPuffle(self, data):
    randomPuffleId = random.randint(1, 1000) # Not stored in the database

    if self.user.Coins < 800:
        return self.sendError(401)

    self.user.Coins -= 800

    puffle = Puffle(Owner=self.user.ID, Name=data.Name, AdoptionDate=time.time(), Type=data.TypeId)
    self.session.add(puffle)
    self.session.commit()

    puffleString = "%d|%s|%d|100|100|100" % (randomPuffleId, data.Name, data.TypeId)
    self.sendXt("pn", self.user.Coins, puffleString)

    pufflesString = getPuffles(self.session, self.user.ID)
    self.sendXt("pgu", pufflesString)

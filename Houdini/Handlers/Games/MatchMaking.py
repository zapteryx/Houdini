from itertools import izip

from twisted.internet import task, reactor

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.CardJitsu import CardJitsu, CardSensei
from Houdini.Handlers.Games.CardFire import CardFire, FireSensei

MatchMakers = {
    951: (CardJitsu, CardSensei, 2, "NinjaRank", 2),
    953: (CardFire, FireSensei, 4, "FireNinjaRank", 4)
}

class MatchMaking(object):

    def __init__(self):
        self.penguins = []
        self.ticker = task.LoopingCall(self.tick)

    def tick(self):
        for roomId, matchMaker in MatchMakers.iteritems():
            cardGame, senseiGame, maxPlayers, sortBy, delay = matchMaker

            penguins = [penguin for penguin in self.penguins if penguin.room.Id == roomId]
            penguins.sort(key=lambda player: getattr(player.user, sortBy))

            matchCount = len(penguins) % maxPlayers
            matchSize = max(2, maxPlayers if matchCount == 0 else matchCount)

            for matchedPenguins in izip(*[iter(penguins)] * matchSize):
                nicknames = "%".join([penguin.user.Nickname + "|" + str(penguin.user.Color) if maxPlayers > 2
                                      else penguin.user.Nickname for penguin in matchedPenguins])

                for penguin in matchedPenguins:
                    penguin.tick -= 1

                    if penguin.tick < -1:
                        for removePenguin in matchedPenguins:
                            removePenguin.sendXt("scard", 0, 0, len(matchedPenguins), 0, nicknames)

                        # delay on the server because start waddle is unreliable!
                        if penguin.tick == -delay:
                            cardGame(list(matchedPenguins), matchSize)
                        matchedPenguins = []
                        break

                for matchedPenguin in matchedPenguins:
                    if maxPlayers > 2:
                        matchedPenguin.sendXt("tmm", len(matchedPenguins), matchedPenguin.tick, nicknames)
                    else:
                        matchedPenguin.sendXt("tmm", matchedPenguin.tick, nicknames)

    def add(self, penguin):
        if penguin not in self.penguins:
            self.penguins.append(penguin)
            penguin.tick = 10
            if len(self.penguins) == 2:
                self.ticker.start(1)

    def remove(self, penguin):
        if penguin in self.penguins:
            self.penguins.remove(penguin)
            if len(self.penguins) == 1:
                self.ticker.stop()

@Handlers.Handle(XT.JoinMatchMaking)
def handleJoinMatchMaking(self, data):
    if self.room.Id in MatchMakers:
        self.server.matchMaker.add(self)
        self.sendXt("jmm", self.user.Username)

@Handlers.Handle(XT.LeaveMatchMaking)
def handleLeaveMatchMaking(self, data):
    self.server.matchMaker.remove(self)

@Handlers.Handle(XT.JoinSensei)
def handleJoinSensei(self, data):
    if self.room.Id in MatchMakers:
        cardGame, senseiGame, maxPlayers, sortBy, delay = MatchMakers[self.room.Id]
        if maxPlayers > 2:
            self.sendXt("scard", 0, 0, 1, 0, self.user.Nickname + "|" + str(self.user.Color))
            reactor.callLater(delay, senseiGame, self)
        else:
            senseiGame(self)
from itertools import izip

from twisted.internet import reactor, task

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.CardJitsu import CardJitsu, CardSensei

class MatchMaking(object):

    def __init__(self):
        self.penguins = []
        self.ticker = task.LoopingCall(self.tick)

    def tick(self):
        self.penguins.sort(key=lambda x: x.user.NinjaRank)
        a = iter(self.penguins)
        for penguins in izip(a, a):
            firstPenguin, secondPenguin = penguins
            for penguin in penguins:
                penguin.tick -= 1
            if firstPenguin.tick == 0 or secondPenguin.tick == 0:
                for penguin in penguins:
                    penguin.sendXt("tmm", -1, firstPenguin.user.Username, secondPenguin.user.Username)
                    penguin.sendXt("scard", 0, 0)
                    self.remove(penguin)
                    continue
                CardJitsu([firstPenguin, secondPenguin], 2)
            for penguin in penguins:
                penguin.sendXt("tmm", penguin.tick, penguin.user.Username)

    def add(self, penguin):
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
    if self.room.Id == 951:
        self.server.matchMaker.add(self)
        self.sendXt("jmm", self.user.Username)

@Handlers.Handle(XT.LeaveMatchMaking)
def handleLeaveMatchMaking(self, data):
    self.server.matchMaker.remove(self)
    self.sendXt("lmm")

@Handlers.Handle(XT.JoinSensei)
def handleJoinSensei(self, data):
    CardSensei(self)
import random

from twisted.internet import reactor

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.CardJitsu import CardEventHandler
from Houdini.Handlers.Games.Waddle import WaddleHandler


class CardFire(object):

    def __init__(self, penguins, seats):
        self.penguins, self.seats = penguins, seats

        self.energy = [6 for _ in xrange(seats)]
        self.state = [0 for _ in xrange(seats)]
        self.boardIds = [0, 8, 4, 12][:seats]
        self.deck = [[] for _ in xrange(seats)]
        self.board = ["b", "s", "w", "f", "c",
                      "s", "f", "w", "b", "s",
                      "w", "f", "c", "w", "s", "f"]

        self.cardsChosen = [None for _ in xrange(seats)]
        self.currentPlayer = 0
        self.spinAmount = 1
        self.moveClockwise = 0
        self.moveAnticlockwise = 0
        self.tabId = 0

        self.currentBattleState = 0
        self.currentBattleElement = None
        self.currentBattleType = "bt"
        self.highestBattleCard = 0
        self.isBattleTie = False

        self.energyBattleSeats = []

        self.boardChoiceTimer = reactor.callLater(22, self.boardTimeout)
        self.battleTimers = []

        self.spin(self.currentPlayer)

        for penguin in self.penguins:
            penguin.joinRoom(997)

            penguin.waddle = self

    def boardTimeout(self):
        currentPlayer = self.penguins[self.currentPlayer]
        currentPlayer.sendXt("zm", "tb")
        chooseBoardId(currentPlayer, self.moveAnticlockwise)

    def battleTimeout(self, seatId):
        timedOutPlayer = self.penguins[seatId]
        timedOutPlayer.sendXt("zm", "tc")
        chooseCard(timedOutPlayer, 1)

    def startBattleTimers(self):
        self.battleTimers = [reactor.callLater(22, self.battleTimeout, seatId)
                             for seatId, player in enumerate(self.penguins)]

    def getWinnerSeatId(self, firstCard, secondCard):
        if firstCard.Element != secondCard.Element:
            ruleSet = {"f": "s", "w": "f", "s": "w"}
            return 0 if ruleSet[firstCard.Element] == secondCard.Element else 1
        elif firstCard.Value > secondCard.Value:
            return 0
        elif secondCard.Value > firstCard.Value:
            return 1
        return -1

    def resolveBattle(self):
        if self.currentBattleType == "be":
            firstSeatId, secondSeatId = self.energyBattleSeats
            cardIndex, secondCardIndex = self.cardsChosen[firstSeatId], self.cardsChosen[secondSeatId]
            firstCard = self.deck[firstSeatId][cardIndex]
            secondCard = self.deck[secondSeatId][secondCardIndex]
            winnerSeatId = self.getWinnerSeatId(firstCard, secondCard)
            if winnerSeatId == 0:
                self.state[firstSeatId], self.state[secondSeatId] = (4, 1)
                self.energy[firstSeatId] += 1
                self.energy[secondSeatId] -= 1
            elif winnerSeatId == 1:
                self.state[firstSeatId], self.state[secondSeatId] = (1, 4)
                self.energy[firstSeatId] -= 1
                self.energy[secondSeatId] += 1
            else:
                self.state[firstSeatId], self.state[secondSeatId] = (2, 2)
            self.currentBattleElement = firstCard.Element if winnerSeatId == 0 else secondCard.Element
        elif self.currentBattleType == "bt":
            for seatId, cardId in enumerate(self.cardsChosen):
                card = self.deck[seatId][cardId]
                if card.Element != self.currentBattleElement:
                    self.state[seatId] = 1
                    self.energy[seatId] -= 1
                elif card.Value == self.highestBattleCard and self.isBattleTie:
                    self.state[seatId] = 2
                elif card.Value == self.highestBattleCard:
                    self.state[seatId] = 3
                else:
                    self.state[seatId] = 1
                    self.energy[seatId] -= 1

    def getNextTurn(self):
        self.currentPlayer = (self.currentPlayer + 1) % self.seats
        return self.currentPlayer

    def spin(self, seatId):
        self.spinAmount = random.randrange(1, 7)
        playerPosition = self.boardIds[seatId]
        self.moveClockwise = (playerPosition + self.spinAmount) % 16
        self.moveAnticlockwise = (playerPosition - self.spinAmount) % 16

    def remove(self, penguin):
        self.penguins.remove(penguin)
        penguin.waddle = None

        for player in self.penguins:
            player.sendXt("cz", penguin.user.Username)

    def getSeatId(self, penguin):
        return self.penguins.index(penguin)

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

class FireMat(CardFire):

    def __init__(self, penguins, seats):
        super(FireMat, self).__init__(penguins, seats)

class FireSensei(CardFire):

    def __init__(self, penguin):
        super(FireSensei, self).__init__([penguin], 2)
        self.penguin = penguin
        penguin.waddle = self

    def remove(self, penguin):
        penguin.waddle = None

@Handlers.Handle(XT.GetGame)
@WaddleHandler(CardFire, FireMat)
def handleGetGame(self, data):
    mySeatId = self.waddle.getSeatId(self)
    self.sendXt("gz", self.waddle.seats, len(self.waddle.penguins))
    self.sendXt("jz", mySeatId)
    self.waddle.deck[mySeatId] = [random.choice(self.cards) for _ in xrange(5)]

    nicknames = ",".join([player.user.Nickname for player in self.waddle.penguins])
    colors = ",".join([str(player.user.Color) for player in self.waddle.penguins])
    energy = ",".join(map(str, self.waddle.energy))
    boardIds = ",".join(map(str, self.waddle.boardIds))
    playerRanks = ",".join([str(player.user.FireNinjaRank) for player in self.waddle.penguins])
    myCardIds = ",".join([str(card.Id) for card in self.waddle.deck[mySeatId]])
    spinResult = ",".join(map(str, [self.waddle.spinAmount,
                                    self.waddle.moveClockwise, self.waddle.moveAnticlockwise]))

    self.sendXt("sz", self.waddle.currentPlayer, nicknames, colors, energy,
                boardIds, myCardIds, spinResult, playerRanks)

@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("is")
def handleInfoClickSpinner(self, data):
    event, seatId, tabId = data.Move
    if not 0 <= int(tabId) <= 6:
        return
    self.waddle.tabId = int(tabId)
    self.waddle.sendXt("zm", "is", seatId, tabId)


def chooseBoardId(self, boardId):
    mySeatId = self.waddle.getSeatId(self)
    self.waddle.boardIds[mySeatId] = int(boardId)
    seatIds = ",".join([str(seatId) for seatId, player in enumerate(self.waddle.penguins)])
    boardIds = ",".join(map(str, self.waddle.boardIds))

    self.waddle.sendXt("zm", "ub", mySeatId, boardIds, self.waddle.tabId)

    element = self.waddle.board[int(boardId)]

    self.waddle.currentBattleType = "bt"

    opponentsOnTab = []
    for seatId, playerBoardId in enumerate(self.waddle.boardIds):
        if seatId != mySeatId and playerBoardId == boardId:
            opponentsOnTab.append(seatId)
    if len(opponentsOnTab) > 0:
        self.waddle.currentBattleState = 2
        self.waddle.currentBattleElement = element
        opponents = ",".join(map(str, opponentsOnTab))
        self.sendXt("zm", "co", opponents)
    elif element in self.waddle.board[1:4]:
        self.waddle.currentBattleElement = element
        self.waddle.currentBattleState = 3
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, seatIds, element)
    elif element == "c":
        self.waddle.currentBattleState = 1
        self.sendXt("zm", "ct")
    elif element == "b":
        self.waddle.currentBattleState = 2
        self.waddle.currentBattleElement = element
        opponents = ",".join([str(seatId) for seatId, player in enumerate(self.waddle.penguins) if seatId != mySeatId])
        self.sendXt("zm", "co", opponents)


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("cb")
def handleChooseBoardId(self, data):
    event, boardId = data.Move
    mySeatId = self.waddle.getSeatId(self)
    if mySeatId == self.waddle.currentPlayer and self.waddle.currentBattleState == 0:
        if int(boardId) != self.waddle.moveClockwise and int(boardId) != self.waddle.moveAnticlockwise:
            return
        self.waddle.boardChoiceTimer.cancel()
        chooseBoardId(self, boardId)


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("co")
def handleChooseOpponent(self, data):
    event, opponentSeatId = data.Move
    if not 0 <= int(opponentSeatId) < self.waddle.seats:
        return
    mySeatId = self.waddle.getSeatId(self)
    if mySeatId == self.waddle.currentPlayer and self.waddle.currentBattleState == 2:
        self.waddle.currentBattleType = "be"
        self.waddle.energyBattleSeats = [mySeatId, int(opponentSeatId)]
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, str(mySeatId) + "," +
                           opponentSeatId, self.waddle.currentBattleElement)
        self.waddle.currentBattleState = 3


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("ct")
def handleChooseTrump(self, data):
    event, element = data.Move
    if element not in self.waddle.board[1:4]:
        return

    mySeatId = self.waddle.getSeatId(self)
    if mySeatId == self.waddle.currentPlayer and self.waddle.currentBattleState == 1:
        self.waddle.currentBattleElement = element
        seatIds = ",".join([str(seatId) for seatId, player in enumerate(self.waddle.penguins)])
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, seatIds, element)
        self.waddle.currentBattleState = 3


def chooseCard(self, cardIndex):
    seatId = self.waddle.getSeatId(self)
    self.waddle.cardsChosen[seatId] = int(cardIndex)

    for player in self.waddle.penguins:
        if player != self:
            player.sendXt("zm", "ic", seatId)

    card = self.waddle.deck[seatId][int(cardIndex)]
    if card.Value == self.waddle.highestBattleCard:
        self.waddle.isBattleTie = True
    if card.Value > self.waddle.highestBattleCard:
        self.waddle.highestBattleCard, self.waddle.isBattleTie = card.Value, False

    if self.waddle.currentBattleType == "bt":
        cardsChosen = None not in self.waddle.cardsChosen
    else:
        firstSeatId, secondSeatId = self.waddle.energyBattleSeats
        cardsChosen = self.waddle.cardsChosen[firstSeatId] is not None \
                      and self.waddle.cardsChosen[secondSeatId] is not None

    if cardsChosen:
        seatIds = ",".join([str(seatId) for seatId, player in enumerate(self.waddle.penguins)])

        cardIds = ",".join(map(str, [self.waddle.deck[seatId][cardIndex].Id
                                     for seatId, cardIndex in enumerate(self.waddle.cardsChosen)]))

        self.waddle.resolveBattle()

        energy = ",".join(map(str, self.waddle.energy))
        states = ",".join(map(str, self.waddle.state))

        for seatId, player in enumerate(self.waddle.penguins):
            myCardIds = ",".join([str(card.Id) for card in self.waddle.deck[seatId]])
            player.sendXt("zm", "rb", seatIds, cardIds, energy, states, self.waddle.currentBattleType + ","
                          + self.waddle.currentBattleElement, myCardIds, "1,2")

        nextSeatId = self.waddle.getNextTurn()
        self.waddle.spin(nextSeatId)
        spinResult = ",".join(map(str, [self.waddle.spinAmount,
                                    self.waddle.moveClockwise, self.waddle.moveAnticlockwise]))

        for seatId, player in enumerate(self.waddle.penguins):
            replaceCardIndex = self.waddle.cardsChosen[seatId]
            self.waddle.deck[seatId][replaceCardIndex] = random.choice(player.cards)
            myCardIds = ",".join([str(card.Id) for card in self.waddle.deck[seatId]])
            player.sendXt("zm", "nt", nextSeatId, spinResult, myCardIds)

        self.waddle.cardsChosen = [None for _ in xrange(self.waddle.seats)]
        self.waddle.boardChoiceTimer = reactor.callLater(22, self.waddle.boardTimeout)
        self.waddle.currentBattleState = 0
        self.waddle.highestBattleCard, self.waddle.isBattleTie = 0, False


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("cc")
def handleSendChooseCard(self, data):
    event, cardIndex = data.Move
    if not 0 <= int(cardIndex) <= 4:
        return
    seatId = self.waddle.getSeatId(self)
    if self.waddle.cardsChosen[seatId] is not None:
        return
    self.waddle.battleTimers[seatId].cancel()
    chooseCard(self, cardIndex)
import random, itertools

from twisted.internet import reactor

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.CardJitsu import CardEventHandler, sendStampsEarned
from Houdini.Handlers.Games.Waddle import WaddleHandler

class FireOpponent(object):

    def __init__(self, seatId, penguin):
        self.seatId, self.penguin = seatId, penguin
        self.energy = 6
        self.state = 0
        self.cardChosen = None
        self.deck = []
        self.ready = False
        self.battleTimeout = None
        self.energyWon = 0


class CardFire(object):

    def __init__(self, penguins, seats):
        self.penguins, self.seats = penguins, seats
        self.board = ["b", "s", "w", "f", "c",
                      "s", "f", "w", "b", "s",
                      "w", "f", "c", "w", "s", "f"]
        self.currentPlayer = None
        self.spinAmount = 1
        self.moveClockwise = 0
        self.moveAnticlockwise = 0
        self.tabId = 0

        self.currentBattleState = 0
        self.currentBattleElement = None
        self.currentBattleType = "bt"
        self.highestBattleCard = 0
        self.isBattleTie = False

        self.finishPositions = [0 for _ in xrange(seats)]
        self.finishPosition = seats

        self.boardIds = [0, 8, 4, 12][:seats]

        self.opponents = []
        self.battleOpponents = []

        self.rankSpeed = 2

        for seatId, penguin in enumerate(self.penguins):
            penguin.joinRoom(997)

            penguin.waddle = self

            fireOpponent = FireOpponent(seatId, penguin)
            self.opponents.append(fireOpponent)

            for _ in xrange(5):
                usableDeck = [card for card in penguin.cards if sum(find.Id == card.Id for find in penguin.cards) >
                              sum(find.Id == card.Id for find in fireOpponent.deck)]
                fireOpponent.deck.append(random.choice(usableDeck))

        self.playerCycle = itertools.cycle(self.opponents)
        self.getNextTurn()

        self.boardTimeout = reactor.callLater(22, self.boardTimeoutCallback)

        self.spin()

    def boardTimeoutCallback(self):
        self.tabId = 1
        self.currentPlayer.penguin.sendXt("zm", "tb")
        chooseBoardId(self.currentPlayer.penguin, self.moveAnticlockwise, True)

    def startBattleTimeouts(self):
        for opponent in self.battleOpponents:
            opponent.battleTimeout = reactor.callLater(22, self.battleTimeoutCallback, opponent)

    def battleTimeoutCallback(self, opponent):
        self.currentPlayer.penguin.sendXt("zm", "tc")
        playableCards = self.getPlayableCards(opponent)
        cardIndex = random.choice(playableCards)
        chooseCard(opponent.penguin, cardIndex)

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
            firstOpponent, secondOpponent = self.battleOpponents[:2]
            firstCard = firstOpponent.deck[firstOpponent.cardChosen]
            secondCard = secondOpponent.deck[secondOpponent.cardChosen]
            winnerSeatId = self.getWinnerSeatId(firstCard, secondCard)
            if winnerSeatId == 0:
                firstOpponent.state, secondOpponent.state = (4, 1)
                firstOpponent.energy += 1
                secondOpponent.energy -= 1
                firstOpponent.energyWon += 1
            elif winnerSeatId == 1:
                firstOpponent.state, secondOpponent.state = (1, 4)
                firstOpponent.energy -= 1
                secondOpponent.energy += 1
                secondOpponent.energyWon += 1
            else:
                firstOpponent.state, secondOpponent.state = (2, 2)
            self.currentBattleElement = firstCard.Element if winnerSeatId == 0 else secondCard.Element
        elif self.currentBattleType == "bt":
            for opponent in self.battleOpponents:
                card = opponent.deck[opponent.cardChosen]
                if card.Element != self.currentBattleElement:
                    opponent.state = 1
                    opponent.energy -= 1
                elif card.Value == self.highestBattleCard and self.isBattleTie:
                    opponent.state = 2
                elif card.Value == self.highestBattleCard:
                    opponent.state = 3
                else:
                    opponent.state = 1
                    opponent.energy -= 1

    def getNextTurn(self):
        self.currentPlayer = next(self.playerCycle)
        while self.currentPlayer not in self.opponents:
            self.currentPlayer = next(self.playerCycle)
        return self.currentPlayer

    def spin(self):
        self.spinAmount = random.randrange(1, 7)
        playerPosition = self.boardIds[self.currentPlayer.seatId]
        self.moveClockwise = (playerPosition + self.spinAmount) % 16
        self.moveAnticlockwise = (playerPosition - self.spinAmount) % 16

    def remove(self, penguin, isQuit=True):
        penguinIndex = self.penguins.index(penguin)
        opponent = self.opponents[penguinIndex]
        if isQuit:
            self.finishPosition -= 1
            for player in self.penguins:
                player.sendXt("zm", "cz", opponent.seatId)

        if opponent == self.currentPlayer and 0 <= self.currentBattleState <= 2:
            self.boardTimeout.cancel()
            if len(self.opponents) > 2:
                self.boardTimeoutCallback()

        if opponent.battleTimeout is not None:
            opponent.battleTimeout.cancel()
            if len(self.opponents) > 2:
                self.battleTimeoutCallback(opponent)

        self.boardIds[penguinIndex] = -1

        self.opponents.remove(opponent)
        self.penguins.remove(penguin)

        if len(self.opponents) == 1:
            opponent = self.opponents[0]
            if self.finishPositions[opponent.seatId] == 0:
                self.finishPositions[opponent.seatId] = 1
                finishPositions = ",".join(str(position) for position in self.finishPositions)
                opponent.penguin.sendXt("zm", "zo", finishPositions)
                self.remove(opponent.penguin, False)

        penguin.waddle = None
        self.seats -= 1
        sendStampsEarned(penguin, 32)

    def getPlayableCards(self, opponent):
        if self.currentBattleType == "bt":
            playableCards = [cardIndex for cardIndex, card in enumerate(opponent.deck)
                    if card.Element == self.currentBattleElement]
            if playableCards:
                return playableCards
        return range(5)

    def getSeatId(self, penguin):
        return self.penguins.index(penguin)

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

class FireMat(CardFire):

    def __init__(self, penguins, seats):
        super(FireMat, self).__init__(penguins, seats)

        self.rankSpeed = 3


@Handlers.Handle(XT.GetGame)
@WaddleHandler(CardFire, FireMat)
def handleGetGame(self, data):
    mySeatId = self.waddle.getSeatId(self)
    self.sendXt("gz", self.waddle.seats, len(self.waddle.penguins))
    self.sendXt("jz", mySeatId)

    nicknames = ",".join([player.user.Nickname for player in self.waddle.penguins])
    colors = ",".join([str(player.user.Color) for player in self.waddle.penguins])
    energy = ",".join([str(opponent.energy) for opponent in self.waddle.opponents])
    boardIds = ",".join(map(str, self.waddle.boardIds))
    playerRanks = ",".join([str(player.user.FireNinjaRank) for player in self.waddle.penguins])
    myCardIds = ",".join([str(card.Id) for card in self.waddle.opponents[mySeatId].deck])
    spinResult = ",".join(map(str, [self.waddle.spinAmount,
                                    self.waddle.moveClockwise, self.waddle.moveAnticlockwise]))

    self.sendXt("sz", self.waddle.currentPlayer.seatId, nicknames, colors, energy,
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


def chooseBoardId(self, boardId, isAutoPlay=False):
    mySeatId = self.waddle.getSeatId(self)
    externalSeatId = self.waddle.opponents[mySeatId].seatId
    if not isAutoPlay or self.waddle.currentBattleState == 0:
        self.waddle.boardIds[externalSeatId] = boardId

        boardIds = ",".join(map(str, self.waddle.boardIds))

        element = self.waddle.board[boardId]

        self.waddle.sendXt("zm", "ub", externalSeatId, boardIds, self.waddle.tabId)

        self.waddle.currentBattleType = "bt"
        self.waddle.battleOpponents = self.waddle.opponents
    else:
        boardId = self.waddle.currentPlayer.boardId
        element = self.waddle.board[boardId]

    opponentsOnTab = []
    for opponent in self.waddle.opponents:
        if opponent.seatId != externalSeatId and self.waddle.boardIds[opponent.seatId] == boardId:
            opponentsOnTab.append(str(opponent.seatId))
    if len(opponentsOnTab) > 0:
        if isAutoPlay:
            self.waddle.currentBattleType = "be"
            opponent = [opponent for opponent in self.waddle.opponents if opponent.seatId != externalSeatId
                        and self.waddle.boardIds[opponent.seatId] == boardId][0]
            self.waddle.battleOpponents = [self.waddle.opponents[mySeatId], opponent]
            self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, str(externalSeatId) + "," +
                               str(opponent.seatId), self.waddle.currentBattleElement)
            self.waddle.currentBattleState = 3
            self.waddle.startBattleTimeouts()
        else:
            self.waddle.currentBattleState = 2
            self.waddle.currentBattleElement = element
            opponents = ",".join(opponentsOnTab)
            self.sendXt("zm", "co", 0, opponents)
    elif element in self.waddle.board[1:4]:
        seatIds = ",".join([str(opponent.seatId) for opponent in self.waddle.opponents])
        self.waddle.currentBattleElement = element
        self.waddle.currentBattleState = 3
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, seatIds, element)
        self.waddle.startBattleTimeouts()
    elif element == "c":
        if isAutoPlay:
            self.waddle.currentBattleElement = random.choice(self.waddle.board[1:4])
            seatIds = ",".join([str(opponent.seatId) for opponent in self.waddle.opponents])
            self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, seatIds, self.waddle.currentBattleElement)
            self.waddle.currentBattleState = 3
            self.waddle.startBattleTimeouts()
        else:
            self.waddle.currentBattleState = 1
            self.sendXt("zm", "ct")
    elif element == "b":
        if isAutoPlay:
            self.waddle.currentBattleType = "be"
            opponent = [opponent for opponent in self.waddle.opponents if opponent.seatId != externalSeatId][0]
            self.waddle.battleOpponents = [self.waddle.opponents[mySeatId], opponent]
            self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, str(externalSeatId) + "," +
                               str(opponent.seatId), self.waddle.currentBattleElement)
            self.waddle.currentBattleState = 3
            self.waddle.startBattleTimeouts()
        else:
            self.waddle.currentBattleState = 2
            self.waddle.currentBattleElement = element
            opponents = ",".join([str(opponent.seatId) for opponent in self.waddle.opponents if opponent.seatId != externalSeatId])
            self.sendXt("zm", "co", 0, opponents)


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("cb")
def handleChooseBoardId(self, data):
    event, boardId = data.Move
    mySeatId = self.waddle.getSeatId(self)
    if mySeatId == self.waddle.opponents.index(self.waddle.currentPlayer) and self.waddle.currentBattleState == 0:
        if int(boardId) != self.waddle.moveClockwise and int(boardId) != self.waddle.moveAnticlockwise:
            return
        self.waddle.boardTimeout.cancel()
        chooseBoardId(self, int(boardId))


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("co")
def handleChooseOpponent(self, data):
    event, opponentSeatId = data.Move
    mySeatId = self.waddle.getSeatId(self)
    externalSeatId = self.waddle.opponents[mySeatId].seatId

    seatIds = [opponent.seatId for opponent in self.waddle.opponents if opponent.seatId != externalSeatId]
    if not int(opponentSeatId) in seatIds:
        return

    if mySeatId == self.waddle.opponents.index(self.waddle.currentPlayer) and self.waddle.currentBattleState == 2:
        self.waddle.currentBattleType = "be"
        self.waddle.battleOpponents = [self.waddle.opponents[mySeatId]]
        for opponent in self.waddle.opponents:
            if opponent.seatId == int(opponentSeatId):
                self.waddle.battleOpponents.append(opponent)
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, str(externalSeatId) + "," +
                           opponentSeatId, self.waddle.currentBattleElement)
        self.waddle.currentBattleState = 3
        self.waddle.startBattleTimeouts()


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("ct")
def handleChooseTrump(self, data):
    event, element = data.Move
    if element not in self.waddle.board[1:4]:
        return

    mySeatId = self.waddle.getSeatId(self)
    if mySeatId == self.waddle.opponents.index(self.waddle.currentPlayer) and self.waddle.currentBattleState == 1:
        self.waddle.currentBattleElement = element
        seatIds = ",".join([str(opponent.seatId) for opponent in self.waddle.opponents])
        self.waddle.sendXt("zm", "sb", self.waddle.currentBattleType, seatIds, element)
        self.waddle.currentBattleState = 3
        self.waddle.startBattleTimeouts()


def chooseCard(self, cardIndex):
    seatId = self.waddle.getSeatId(self)
    waddle = self.waddle
    if cardIndex not in waddle.getPlayableCards(waddle.opponents[seatId]):
        return

    waddle.opponents[seatId].cardChosen = cardIndex
    waddle.opponents[seatId].battleTimeout = None

    for opponent in self.waddle.opponents:
        if opponent.penguin != self:
            opponent.penguin.sendXt("zm", "ic", waddle.opponents[seatId].seatId)

    card = waddle.opponents[seatId].deck[cardIndex]
    if card.Value == waddle.highestBattleCard:
        self.waddle.isBattleTie = True
    if card.Value > waddle.highestBattleCard:
        waddle.highestBattleCard, waddle.isBattleTie = card.Value, False

    cardsChosen = None not in [opponent.cardChosen for opponent in waddle.battleOpponents]
    if cardsChosen:
        seatIds = ",".join([str(opponent.seatId) for opponent in waddle.battleOpponents])

        cardIds = ",".join([str(opponent.deck[opponent.cardChosen].Id) for opponent in waddle.battleOpponents])

        waddle.resolveBattle()

        energy = ",".join([str(opponent.energy) for opponent in waddle.battleOpponents])
        states = ",".join([str(opponent.state) for opponent in waddle.battleOpponents])

        for opponent in waddle.opponents:
            if not opponent.energy:
                waddle.finishPositions[opponent.seatId] = waddle.finishPosition
                waddle.finishPosition -= 1
            if waddle.finishPositions.count(0) == 1:
                winnerIndex = waddle.finishPositions.index(0)
                waddle.finishPositions[winnerIndex] = 1

        finishPositions = ",".join(str(position) for position in waddle.finishPositions)

        for opponent in list(waddle.opponents):
            myCardIds = ",".join([str(card.Id) for card in opponent.deck])
            opponent.penguin.sendXt("zm", "rb", seatIds, cardIds, energy, states, waddle.currentBattleType + ","
                          + waddle.currentBattleElement, myCardIds, finishPositions)

            if not opponent.energy or not waddle.finishPositions.count(0):
                if 0 in waddle.finishPositions:
                    finishPositions = [1]*len(waddle.finishPositions)
                    finishPositions[opponent.seatId] = waddle.finishPositions[opponent.seatId]
                    finishPositions = ",".join(str(position) for position in finishPositions)

                playerFinishPosition = waddle.finishPositions[opponent.seatId]

                if playerFinishPosition == 1:
                    opponent.penguin.user.FireMatchesWon += 1
                    if opponent.penguin.user.FireMatchesWon >= 10:
                        opponent.penguin.addStamp(252, True)
                    if opponent.penguin.user.FireMatchesWon >= 50:
                        opponent.penguin.addStamp(268, True)
                    if opponent.energy >= 6:
                        opponent.penguin.addStamp(260, True)

                if opponent.energyWon >= 1:
                    opponent.penguin.addStamp(254, True)
                if opponent.energyWon >= 3:
                    opponent.penguin.addStamp(266, True)

                if opponent.penguin.user.FireNinjaRank < 4:
                    currentRank = opponent.penguin.user.FireNinjaRank
                    progressPoints = 100 / waddle.rankSpeed / (currentRank + 1) / playerFinishPosition
                    opponent.penguin.user.FireNinjaProgress += progressPoints

                    if opponent.penguin.user.FireNinjaProgress >= 100:
                        awardItems = [6025, 4120, 2013, 1086]
                        rankStamps = {2: 256, 4: 262}
                        opponent.penguin.user.FireNinjaRank += 1

                        if opponent.penguin.user.FireNinjaRank in rankStamps:
                            opponent.penguin.addStamp(rankStamps[opponent.penguin.user.FireNinjaRank], True)

                        opponent.penguin.sendXt("zm", "nr", 0, opponent.penguin.user.FireNinjaRank)
                        opponent.penguin.addItem(awardItems[opponent.penguin.user.FireNinjaRank - 1], sendXt=False)

                    opponent.penguin.user.FireNinjaProgress %= 100

                opponent.penguin.sendXt("zm", "zo", finishPositions)
                waddle.remove(opponent.penguin, False)

        waddle.currentBattleState = 0
        waddle.highestBattleCard, waddle.isBattleTie = 0, False


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("ir")
def handleInfoReadySync(self, data):
    seatId = self.waddle.getSeatId(self)
    self.waddle.opponents[seatId].ready = True

    if self.waddle.currentBattleState != 0:
        return

    if all([opponent.ready for opponent in self.waddle.opponents]):
        nextPlayer = self.waddle.getNextTurn()
        self.waddle.spin()
        spinResult = ",".join(map(str, [self.waddle.spinAmount,
                                        self.waddle.moveClockwise, self.waddle.moveAnticlockwise]))

        for opponent in self.waddle.opponents:
            if opponent in self.waddle.battleOpponents:
                usableDeck = [card for card in opponent.penguin.cards if
                              sum(find.Id == card.Id for find in opponent.penguin.cards) >
                              sum(find.Id == card.Id for find in opponent.deck)]
                opponent.deck[opponent.cardChosen] = random.choice(usableDeck)

            myCardIds = ",".join([str(card.Id) for card in opponent.deck])
            opponent.penguin.sendXt("zm", "nt", nextPlayer.seatId, spinResult, myCardIds)

        self.waddle.boardTimeout = reactor.callLater(22, self.waddle.boardTimeoutCallback)

        for opponent in self.waddle.opponents:
            opponent.cardChosen = None
            opponent.ready = False


@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardFire, FireMat)
@CardEventHandler("cc")
def handleSendChooseCard(self, data):
    event, cardIndex = data.Move
    if self.waddle.currentBattleState != 3:
        return

    if not 0 <= int(cardIndex) <= 4:
        return
    seatId = self.waddle.getSeatId(self)
    if self.waddle.opponents[seatId].cardChosen is not None:
        return
    self.waddle.opponents[seatId].battleTimeout.cancel()
    chooseCard(self, int(cardIndex))


@Handlers.Handle(XT.LeaveGame)
@WaddleHandler(CardFire, FireMat)
def handleLeaveGame(self, data):
    sendStampsEarned(self, 32)

class FireSensei(CardFire):

    def __init__(self, penguin):
        super(FireSensei, self).__init__([penguin], 2)
        self.penguin = penguin
        penguin.waddle = self

        self.senseiOpponent = FireOpponent(1, penguin)
        self.opponents.append(self.senseiOpponent)

    def boardTimeoutCallback(self):
        pass

    def startBattleTimeouts(self):
        pass

    def battleTimeoutCallback(self, opponent):
        pass

    def remove(self, penguin, isQuit=False):
        penguin.waddle = None


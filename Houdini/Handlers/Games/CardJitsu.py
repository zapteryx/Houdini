import random, itertools, math, copy

from Houdini.Handlers import Handlers, XT
from Houdini.Handlers.Games.Waddle import WaddleHandler

class CardJitsu(object):

    def __init__(self, penguins, seats):
        self.penguins, self.seats = penguins, seats
        self.deck = [{}, {}]
        self.cardsChosen = [False, False]
        self.playerCards = [{"f":[], "w":[], "s": []},
                            {"f":[], "w":[], "s": []}]
        self.cardId = 1
        self.powers = {}
        self.discards = []

        self.rankSpeed = 2

        for penguin in self.penguins:
            penguin.joinRoom(998)

            penguin.waddle = self

    def getWinningCards(self, seatId):
        playerCards = self.playerCards[seatId]
        for element, cards in playerCards.iteritems():
            colorCards, colors = [], []
            for card in cards:
                if card.Color not in colors:
                    colorCards.append(card)
                    colors.append(card.Color)
                    if len(colorCards) == 3:
                        return colorCards, 0
        elements = playerCards.values()
        combos = list(itertools.product(*elements))
        for combo in combos:
            colors = [card.Color for card in combo]
            if len(set(colors)) == 3:
                return combo, 1
        return False, -1

    def hasCardsToPlay(self, seatId):
        powerLimiters = {13: "s", 14: "f", 15: "w"}
        for powerId, element in powerLimiters.iteritems():
            if powerId in self.powers:
                powerCard = self.powers[powerId]
                if powerCard.Opponent == seatId:
                    opponentDeck = self.deck[powerCard.Opponent]
                    for cardId, card in opponentDeck.iteritems():
                        if card.Element != element:
                            return True
                    return False
        return True

    def getWinnerSeatId(self, firstCard, secondCard):
        if firstCard.Element != secondCard.Element:
            ruleSet = {"f": "s", "w": "f", "s": "w"}
            return 0 if ruleSet[firstCard.Element] == secondCard.Element else 1
        elif firstCard.Value > secondCard.Value:
            return 0
        elif secondCard.Value > firstCard.Value:
            return 1
        return -1

    def discardOpponentCard(self, powerId, opponentSeatId):
        opponentCards = self.playerCards[opponentSeatId]
        discardElements = {4: "s", 5: "w", 6: "f"}
        discardColors = {7: "r", 8: "b", 9: "g", 10: "y", 11: "o", 12: "p"}
        if powerId in discardElements:
            elementToDiscard = discardElements[powerId]
            if len(opponentCards[elementToDiscard]) > 0:
                cardToDiscard = self.playerCards[opponentSeatId][elementToDiscard][-1]
                self.discards.append(cardToDiscard.gameId)
                del self.playerCards[opponentSeatId][elementToDiscard][-1]
                return
        if powerId in discardColors:
            colorToDiscard = discardColors[powerId]
            for element, cards in opponentCards.iteritems():
                for index, card in enumerate(cards):
                    if card.Color == colorToDiscard:
                        cardToDiscard = self.playerCards[opponentSeatId][element][index]
                        self.discards.append(cardToDiscard.gameId)
                        del self.playerCards[opponentSeatId][element][index]
                        return

    def replaceOpponentCard(self, powerId, firstCard, secondCard, seatId):
        replacements = {16: ["w", "f"], 17: ["s", "w"], 18: ["f", "s"]}
        for replacePowerId, replacement in replacements.iteritems():
            if powerId == replacePowerId:
                original, replace = replacement
                if seatId == 1 and firstCard.Element == original:
                    firstCard.Element = replace
                if seatId == 0 and secondCard.Element == original:
                    secondCard.Element = replace

    def adjustCardValues(self, firstCard, secondCard,):
        for powerId, powerCard in self.powers.iteritems():
            if powerCard.PowerId == 1 and firstCard.Element == secondCard.Element:
                    firstCard.Value = 1
                    secondCard.Value = 1
            if powerCard.PowerId == 2:
                if powerCard.Player == 0:
                    firstCard.Value += 2
                else:
                    secondCard.Value += 2
            if powerCard.PowerId == 3:
                if powerCard.Player == 0:
                    secondCard.Value -= 2
                else:
                    firstCard.Value -= 2

    def getRoundWinner(self):
        firstCard, secondCard = self.cardsChosen
        winnerSeatId = self.getWinnerSeatId(firstCard, secondCard)

        self.adjustCardValues(firstCard, secondCard)

        self.powers = {}

        for cardSeatId, card in enumerate(self.cardsChosen):
            powerId = card.PowerId
            if not powerId:
                continue

            opponentSeatId = 1 if cardSeatId == 0 else 0

            card.Player = cardSeatId
            card.Opponent = opponentSeatId

            onPlayed = powerId in (1, 13, 16, 17, 18)
            onScored = not onPlayed
            currentRound = powerId in (4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18)
            nextRound = not currentRound

            if onPlayed and nextRound:
                self.powers[powerId] = card

            if onScored and cardSeatId == winnerSeatId:
                if nextRound:
                    self.powers[powerId] = card
                if currentRound:
                    self.discardOpponentCard(powerId, opponentSeatId)
            if onPlayed and currentRound:
                self.replaceOpponentCard(powerId, firstCard, secondCard, card.Player)

        winnerSeatId = self.getWinnerSeatId(firstCard, secondCard)

        self.cardsChosen = [False]*2
        return winnerSeatId

    def remove(self, penguin):
        self.penguins.remove(penguin)
        penguin.waddle = None

        for player in self.penguins:
            player.sendXt("cz", penguin.user.Username)

    def reset(self):
        for penguin in self.penguins:
            self.penguins.remove(penguin)
            penguin.waddle = None

    def getSeatId(self, penguin):
        return self.penguins.index(penguin)

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

    def cardJitsuWin(self, winnerSeatId):
        for seatId, penguin in enumerate(self.penguins):
            if penguin.user.NinjaRank == 0:
                penguin.user.NinjaProgress += 100
            elif penguin.user.NinjaRank < 9:
                points = math.floor(100 / (penguin.user.NinjaRank * self.rankSpeed
                    if winnerSeatId == seatId else self.rankSpeed * 2))
                penguin.user.NinjaProgress += points
            if penguin.user.NinjaProgress >= 100:
                penguin.user.NinjaRank += 1
                penguin.user.NinjaProgress = 0
                penguin.sendXt("cza", penguin.user.NinjaRank)
                rankAwards = [4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 104]

                penguin.inventory.append(rankAwards[penguin.user.NinjaRank - 1])
                stringifiedInventory = map(str, penguin.inventory)
                penguin.user.Inventory = "%".join(stringifiedInventory)

                beltPostcards = {1: 177, 5: 178, 9: 179}
                if penguin.user.NinjaRank in beltPostcards:
                    penguin.receiveSystemPostcard(beltPostcards[penguin.user.NinjaRank])
                beltStamps = {1: 230, 5: 232, 9: 234, 10: 236}
                if penguin.user.NinjaRank in beltStamps:
                    penguin.addStamp(beltStamps[penguin.user.NinjaRank], True)
            self.sendStampsEarned(penguin)

    def sendStampsEarned(self, penguin):
        cardStamps = penguin.server.stampGroups[38].StampsById
        myStamps = map(int, penguin.user.Stamps.split("|")) if penguin.user.Stamps else []
        collectedStamps = []
        for myStamp in myStamps:
            if myStamp in cardStamps:
                collectedStamps.append(myStamp)
        collectedStamps = [str(myStamp) for myStamp in myStamps if myStamp in cardStamps]
        totalStamps = len(collectedStamps)
        totalStampsGame = len(cardStamps)
        collectedStampsString = "|".join(collectedStamps)
        penguin.sendXt("cjsi", collectedStampsString, totalStamps, totalStampsGame)

class CardMat(CardJitsu):

    def __init__(self, penguins, seats):
        super(CardMat, self).__init__(penguins, seats)

        self.rankSpeed = 3

class CardSensei(CardJitsu):

    def __init__(self, penguin):
        super(CardSensei, self).__init__([penguin], 2)

        self.penguin = penguin
        self.senseiMove = {}
        self.colors = []

        penguin.waddle = self

    def remove(self, penguin):
        penguin.waddle = None

    def beatsCard(self, cardCheck, cardPlay):
        if cardCheck.Element != cardPlay.Element:
            ruleSet = {"f": "s", "w": "f", "s": "w"}
            return True if ruleSet[cardCheck.Element] == cardPlay.Element else False
        elif cardCheck.Value > cardPlay.Value:
            return True
        return False

    def getWinCard(self, card):
        self.colors = [] if len(self.colors) >= 6 else self.colors
        for cardCheck in self.penguin.server.cards.values():
            if self.beatsCard(cardCheck, card) and cardCheck.Color not in self.colors:
                self.colors.append(cardCheck.Color)
                return cardCheck

def CardEventHandler(event):
    def handlerFunction(function):
        def handler(penguin, data):
            moveEvent = data.Move[0]
            if event == moveEvent:
                function(penguin, data)
            return function
        return handler
    return handlerFunction

@Handlers.Handle(XT.GetGame)
@WaddleHandler(CardJitsu, CardMat)
def handleGetGame(self, data):
    seatId = self.waddle.getSeatId(self)
    self.sendXt("gz", self.waddle.seats, len(self.waddle.penguins))
    self.sendXt("jz", seatId, self.user.Username, self.user.Color, self.user.NinjaRank)

@Handlers.Handle(XT.UpdateGame)
@WaddleHandler(CardJitsu, CardMat)
def handleUpdateGame(self, data):
    players = []
    for seatId, player in enumerate(self.waddle.penguins):
        players.append("|".join(map(str, [seatId, player.user.Username, player.user.Color, player.user.NinjaRank])))

    self.sendXt("uz", "%".join(players))
    self.sendXt("sz")

@Handlers.Handle(XT.GetGame)
@WaddleHandler(CardSensei)
def handleGetGame(self, data):
    self.sendXt("gz", 2, 2)
    self.sendXt("jz", 1, self.user.Username, self.user.Color, self.user.NinjaRank)

@Handlers.Handle(XT.UpdateGame)
@WaddleHandler(CardSensei)
def handleUpdateGame(self, data):
    players = ["0|Sensei|14|10", "|".join(map(str, [1, self.user.Username, self.user.Color, self.user.NinjaRank]))]
    self.sendXt("uz", "%".join(players))
    self.sendXt("sz")

@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardSensei)
@CardEventHandler("deal")
def handleSendMove(self, data):
    event, move = data.Move
    cardStrings = []
    senseiCardStrings = []
    while len(self.waddle.deck[1]) < 5:
        waddleDeck = list(self.waddle.deck[1].values())
        usableDeck = [card for card in self.deck if not card.PowerId or self.user.NinjaRank >= 9 and
                      sum(find.Id == card.Id for find in self.deck) >
                      sum(find.Id == card.Id for find in waddleDeck)]
        card = random.choice(usableDeck)
        if self.user.NinjaRank < 9:
            senseiCard = copy.copy(self.waddle.getWinCard(card))
        else:
            senseiCard = copy.copy(random.choice(self.server.cards.values()))

        card = copy.copy(card)

        self.waddle.deck[0][self.waddle.cardId] = senseiCard
        senseiCard.gameId = self.waddle.cardId

        senseiCardStrings.append(str(self.waddle.cardId) + "|" + senseiCard.getString())
        self.waddle.cardId += 1

        self.waddle.deck[1][self.waddle.cardId] = card
        card.gameId = self.waddle.cardId

        cardStrings.append(str(self.waddle.cardId) + "|" + card.getString())
        self.waddle.senseiMove[self.waddle.cardId] = self.waddle.cardId - 1

        self.waddle.cardId += 1

    senseiCardsStrings = "%".join(senseiCardStrings)
    self.sendXt("zm", event, 0, senseiCardsStrings)

    cardsString = "%".join(cardStrings)
    self.sendXt("zm", event, 1, cardsString)

@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardSensei)
@CardEventHandler("pick")
def handleSendMove(self, data):
    event, cardId = data.Move
    if int(cardId) not in self.waddle.deck[1]:
        return

    self.waddle.cardsChosen[0] = self.waddle.deck[0][self.waddle.senseiMove[int(cardId)]]
    self.waddle.cardsChosen[1] = self.waddle.deck[1][int(cardId)]

    del self.waddle.deck[0][self.waddle.senseiMove[int(cardId)]]
    del self.waddle.deck[1][int(cardId)]

    self.sendXt("zm", event, 0, self.waddle.senseiMove[int(cardId)])
    self.sendXt("zm", event, 1, int(cardId))

    if all(self.waddle.cardsChosen):
        firstCard, secondCard = self.waddle.cardsChosen
        winnerSeatId = self.waddle.getRoundWinner()
        if winnerSeatId == -1:
            self.sendXt("zm", "judge", winnerSeatId)
            return

        winningCard = firstCard if winnerSeatId == 0 else secondCard
        loserSeatId = 1 if winnerSeatId == 0 else 0

        if winningCard.PowerId:
            self.sendXt("zm", "power", winnerSeatId, loserSeatId, winningCard.PowerId,
                               "%".join(map(str, self.waddle.discards)))
            self.waddle.discards = []

        self.sendXt("zm", "judge", winnerSeatId)

        self.waddle.playerCards[winnerSeatId][winningCard.Element].append(winningCard)

        winningCards, winMethod = self.waddle.getWinningCards(winnerSeatId)

        if winningCards:
            cardIds = "%".join(map(str, [card.gameId for card in winningCards]))
            self.sendXt("czo", 0, winnerSeatId, cardIds)
            if winnerSeatId == 1 and self.user.NinjaRank < 10:
                self.user.NinjaProgress += 100
                self.waddle.cardJitsuWin(winnerSeatId)
            self.waddle = None
            return

        for seatId in (0, 1):
            hasCards = self.waddle.hasCardsToPlay(seatId)
            if not hasCards:
                winnerSeatId = 1 if seatId == 0 else 1
                self.sendXt("czo", 0, winnerSeatId)
                if winnerSeatId == 1 and self.user.NinjaRank < 10:
                    self.user.NinjaProgress += 100
                    self.waddle.cardJitsuWin(winnerSeatId)
                self.waddle = None
                return

@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardJitsu, CardMat)
@CardEventHandler("deal")
def handleSendMove(self, data):
    event, move = data.Move
    seatId = self.waddle.getSeatId(self)
    opponentSeatId = 1 if seatId == 0 else 0
    opponent = self.waddle.penguins[opponentSeatId]
    cardStrings = []

    while len(self.waddle.deck[seatId]) < 5:
        waddleDeck = list(self.waddle.deck[seatId].values())
        usableDeck = [card for card in self.deck if sum(find.Id == card.Id for find in self.deck) >
                      sum(find.Id == card.Id for find in waddleDeck)]
        card = random.choice(usableDeck)
        self.waddle.deck[seatId][self.waddle.cardId] = copy.copy(card)
        self.waddle.deck[seatId][self.waddle.cardId].gameId = self.waddle.cardId
        cardStrings.append(str(self.waddle.cardId) + "|" + card.getString())
        self.waddle.cardId += 1

    cardsString = "%".join(cardStrings)

    self.sendXt("zm", event, seatId, cardsString)
    opponent.sendXt("zm", event, seatId, cardsString)

@Handlers.Handle(XT.SendMove)
@WaddleHandler(CardJitsu, CardMat)
@CardEventHandler("pick")
def handleSendMove(self, data):
    event, cardId = data.Move
    seatId = self.waddle.getSeatId(self)
    opponentSeatId = 1 if seatId == 0 else 0
    opponent = self.waddle.penguins[opponentSeatId]
    if int(cardId) not in self.waddle.deck[seatId]:
        return
    if self.waddle.cardsChosen[seatId]:
        return
    self.waddle.cardsChosen[seatId] = self.waddle.deck[seatId][int(cardId)]
    del self.waddle.deck[seatId][int(cardId)]
    self.sendXt("zm", event, seatId, int(cardId))
    opponent.sendXt("zm", event, seatId, int(cardId))
    if all(self.waddle.cardsChosen):
        firstCard, secondCard = self.waddle.cardsChosen
        winnerSeatId = self.waddle.getRoundWinner()
        if winnerSeatId == -1:
            self.waddle.sendXt("zm", "judge", winnerSeatId)
            return

        winningCard = firstCard if winnerSeatId == 0 else secondCard
        loserSeatId = 1 if winnerSeatId == 0 else 0

        if winningCard.PowerId:
            self.waddle.sendXt("zm", "power", winnerSeatId, loserSeatId, winningCard.PowerId,
                               "%".join(map(str, self.waddle.discards)))
            self.waddle.discards = []

        self.waddle.sendXt("zm", "judge", winnerSeatId)

        self.waddle.playerCards[winnerSeatId][winningCard.Element].append(winningCard)

        winningCards, winMethod = self.waddle.getWinningCards(winnerSeatId)

        if firstCard.Id == 256 or secondCard.Id == 256:
            for penguin in self.waddle.penguins:
                penguin.addStamp(246, True)

        if winningCards:
            cardIds = "%".join(map(str, [card.gameId for card in winningCards]))
            self.waddle.sendXt("czo", 0, winnerSeatId, cardIds)
            self.waddle.cardJitsuWin(winnerSeatId)

            self.waddle.penguins[winnerSeatId].addStamp([244, 242][winMethod], True)
            if all(cards == list() for cards in self.waddle.playerCards[loserSeatId].values()):
                self.waddle.penguins[winnerSeatId].addStamp(238, True)
            if len([card for cards in self.waddle.playerCards[winnerSeatId].values() for card in cards]) >= 9:
                self.waddle.penguins[winnerSeatId].addStamp(248, True)

            self.waddle.reset()
            return

        for seatId, player in enumerate(self.waddle.penguins):
            if not self.waddle.hasCardsToPlay(seatId):
                winnerSeatId = 1 if seatId == 0 else 1
                self.waddle.cardJitsuWin(winnerSeatId)
                self.waddle.sendXt("czo", 0, winnerSeatId)
                self.waddle.reset()
                return
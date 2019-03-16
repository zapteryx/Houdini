from Houdini.Handlers import Handlers, XT

import random

@Handlers.Handle(XT.GetGameAgain)
def handleGetGame(self, data):
    if self.room.Id == 963 and self.user.AgentStatus:
        games = range(1, 11)
        medals = range(1, 6)
        chosenGames = []

        while len(chosenGames) < 3:
            choice = random.choice(games)
            if choice not in chosenGames:
                chosenGames.append(choice)

        self.sendXt("zr", ",".join(map(str, chosenGames)), random.choice(medals))

@Handlers.Handle(XT.GameComplete)
def handleGameComplete(self, data):
    if self.room.Id == 963 and self.user.AgentStatus:
        medals = data.Medals
        self.user.AgentMedals += medals
        self.user.CareerMedals += medals

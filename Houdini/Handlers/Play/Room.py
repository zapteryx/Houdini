import random
from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.GetCoinReward)
def handleGetCoinRewards(self, data):
    if random.random() < 0.2:
        coins = random.choice([1, 2, 5, 10, 20, 50, 100])
        self.user.Coins += coins
        self.session.commit()
        self.sendXt("cdu", coins, self.user.Coins)
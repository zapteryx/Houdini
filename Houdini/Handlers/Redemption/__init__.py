from sqlalchemy import and_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import PenguinRedemption, RedemptionBook

@Handlers.Handle(XT.JoinRedemption)
@Handlers.Throttle(-1)
def handleJoinRedemption(self, data):
    loginArray = data.LoginData.split("|")
    if int(loginArray[0]) != self.user.ID:
        return self.transport.loseConnection()

    if loginArray[3] == "":
        return self.transport.loseConnection()

    if loginArray[3] != self.user.LoginKey:
        self.user.LoginKey = ""
        return self.sendErrorAndDisconnect(101)

    redeemedBooks = self.session.query(PenguinRedemption.CodeID) \
                    .filter(and_(PenguinRedemption.PenguinID == self.user.ID,PenguinRedemption.CodeID < 50)) \
                    .all()
    self.redeemedBookIds = [bookId for bookId, in redeemedBooks]

    self.user.TBValidation = False
    self.user.isRedeemingPuffle = False
    self.sendXt("rjs", ",".join(map(str, self.redeemedBookIds)), "", self.user.Member)

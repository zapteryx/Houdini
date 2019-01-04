from Houdini.Handlers import Handlers, XT

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

    self.user.TBValidation = False
    self.sendXt("rjs", "", 1)

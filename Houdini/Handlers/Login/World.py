from Houdini.Handlers import Handlers, XML
from Houdini.Data.Penguin import Penguin
from Houdini.Crypto import Crypto

@Handlers.Handle(XML.Login)
def handleLogin(self, data):
    username = data.Username
    password = data.Password

    self.logger.info("{0} is attempting to login..".format(username))

    self.session.commit()
    user = self.session.query(Penguin).filter_by(Username=username).first()

    if user is None:
        return self.sendErrorAndDisconnect(100)

    if not user.LoginKey:
        return self.transport.loseConnection()

    loginHash = Crypto.encryptPassword(user.LoginKey + self.randomKey) + user.LoginKey

    if password != loginHash:
        self.logger.debug("{} failed to login.".format(username))

        return self.sendErrorAndDisconnect(101)

    if user.ID in self.server.players:
        self.server.players[user.ID].transport.loseConnection()

    self.logger.info("{} logged in successfully".format(username))

    self.session.add(user)
    self.user = user

    self.agentStatus, self.fieldOpStatus, \
        self.careerPoints, self.agentPoints = map(int, self.user.EPF.split(","))

    # Add them to the Redis set
    self.server.redis.sadd("%s.players" % self.server.serverName, self.user.ID)
    self.server.redis.incr("%s.population" % self.server.serverName)

    self.sendXt("l")

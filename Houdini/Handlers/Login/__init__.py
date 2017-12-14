from Houdini.Handlers import Handlers, XML

@Handlers.Handle(XML.VersionCheck)
def handleVersionCheck(self, data):
    if not data.Version == 153:
        self.sendXml({"body": {"action": "apiKO", "r": "0"}})
        self.transport.loseConnection()
    else:
        self.sendXml({"body": {"action": "apiOK", "r": "0"}})

@Handlers.Handle(XML.RandomKey)
def handleRandomKey(self, data):
    self.randomKey = "houdini"
    self.sendXml({"body": {"action": "rndK", "r": "-1"}, "k": self.randomKey})
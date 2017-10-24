from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.GetIgnoreList)
def handleGetIgnoreList(self, data):
    ignoreArray = self.user.Ignore.split("%")

    for ignoreUser in ignoreArray:
        try:
            ignoreId, ignoreName = ignoreUser.split("|")
            self.ignore[int(ignoreId)] = ignoreName
        except ValueError as valueError:
            self.logger.debug('handleGetIgnoreList: %s', valueError.message)
            break

    self.sendXt("gn", self.user.Ignore)

@Handlers.Handle(XT.AddIgnore)
def handleAddIgnore(self, data):
    if data.PlayerId in self.buddies:
        return

    if data.PlayerId in self.ignore:
        return

    ignoreUser = self.session.query(Penguin.Username).\
        filter(Penguin.ID == data.PlayerId).first()

    self.ignore[data.PlayerId] = ignoreUser.Username
    ignoreString = "%".join(["%s|%s" % (ignoreId, ignoreUsername) for (ignoreId, ignoreUsername) in self.ignore.items()])
    self.user.Ignore = ignoreString
    self.session.commit()

    self.sendXt("gn", self.user.Ignore)

@Handlers.Handle(XT.RemoveIgnore)
def handleRemoveIgnore(self, data):
    if data.PlayerId not in self.ignore:
        return

    del self.ignore[data.PlayerId]
    ignoreString = "%".join(["%s|%s" % (ignoreId, ignoreUsername) for (ignoreId, ignoreUsername) in self.ignore.items()])
    self.user.Ignore = ignoreString
    self.session.commit()

    self.sendXt("gn", self.user.Ignore)
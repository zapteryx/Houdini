from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin, IgnoreList

@Handlers.Handle(XT.GetIgnoreList)
@Handlers.Throttle(-1)
def handleGetIgnoreList(self, data):
    ignoreString = "%".join(["{}|{}".format(ignoreId, ignoreUsername) for ignoreId, ignoreUsername in self.ignore.items()])
    self.sendXt("gn", ignoreString)

@Handlers.Handle(XT.AddIgnore)
def handleAddIgnore(self, data):
    if data.PlayerId in self.buddies:
        return

    if data.PlayerId in self.ignore:
        return


    self.ignore[data.PlayerId] = ignoreUser.Username


@Handlers.Handle(XT.RemoveIgnore)
def handleRemoveIgnore(self, data):
    if data.PlayerId not in self.ignore:
        return

    del self.ignore[data.PlayerId]


import datetime

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Inventory

@Handlers.Handle(XT.GetAgentStatus)
def handleGetAgentStatus(self, data):
    self.sendXt("epfga", self.user.AgentStatus)

@Handlers.Handle(XT.SetAgentStatus)
@Handlers.Throttle(-1)
def handleSetAgentStatus(self, data):
    if not self.user.AgentStatus:
        self.user.AgentStatus = 1
        self.sendXt("epfsa", self.user.AgentStatus)

@Handlers.Handle(XT.GetFieldOpStatus)
def handleGetFieldOpStatus(self, data):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    if self.user.LastFieldOp.date() < monday:
        self.user.FieldOpStatus = 0
    self.sendXt("epfgf", self.user.FieldOpStatus)

@Handlers.Handle(XT.SetFieldOpStatus)
def handleSetFieldOpStatus(self, data):
    if data.FieldOpStatus > 2:
        return

    if self.user.FieldOpStatus + 1 == data.FieldOpStatus:
        self.user.FieldOpStatus += 1
        if self.user.FieldOpStatus == 2:
            self.user.CareerMedals += 2
            self.user.AgentMedals += 2

        self.sendXt("epfsf", self.user.FieldOpStatus)
        self.user.LastFieldOp = datetime.datetime.now()

@Handlers.Handle(XT.GetEpfPoints)
def handleGetEpfPoints(self, data):
    self.sendXt("epfgr", self.user.CareerMedals, self.user.AgentMedals)

@Handlers.Handle(XT.BuyEpfItem)
def handleBuyEpfItem(self, data):
    if self.server.items.isItemEPF(data.ItemId):
        if data.ItemId not in self.server.items:
            return self.sendError(402)
        elif data.ItemId not in self.server.availableClothing["EPF"]:
            return self.sendError(402)
        elif data.ItemId in self.inventory:
            return self.sendError(400)

        itemCost = self.server.items.getCost(data.ItemId)

        if self.user.AgentMedals < itemCost:
            return self.sendError(401)

        self.inventory.append(data.ItemId)

        self.session.add(Inventory(PenguinID=self.user.ID, ItemID=data.ItemId))

        self.user.AgentMedals -= itemCost
        self.sendXt("epfai", self.user.AgentMedals)

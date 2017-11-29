from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin

@Handlers.Handle(XT.GetAgentStatus)
def handleGetAgentStatus(self, data):
    self.sendXt("epfga", self.agentStatus)

@Handlers.Handle(XT.SetAgentStatus)
@Handlers.Throttle(-1)
def handleSetAgentStatus(self, data):
    self.agentStatus = 1
    self.user.EPF = ",".join(map(str, [self.agentStatus, self.fieldOpStatus,
                                       self.careerPoints, self.agentPoints]))
    self.session.commit()
    self.sendXt("epfsa", self.agentStatus)

@Handlers.Handle(XT.GetFieldOpStatus)
def handleGetFieldOpStatus(self, data):
    self.sendXt("epfgf", self.fieldOpStatus)

@Handlers.Handle(XT.SetFieldOpStatus)
def handleSetFieldOpStatus(self, data):
    if data.FieldOpStatus > 2:
        return

    if self.fieldOpStatus + 1 == data.FieldOpStatus:
        self.fieldOpStatus += 1
        if self.fieldOpStatus == 2:
            self.careerPoints += 2
            self.agentPoints += 2

        self.sendXt("epfsf", self.fieldOpStatus)
        self.user.EPF = ",".join(map(str, [self.agentStatus, self.fieldOpStatus,
                                       self.careerPoints, self.agentPoints]))
        self.session.commit()

@Handlers.Handle(XT.GetEpfPoints)
def handleGetEpfPoints(self, data):
    self.sendXt("epfgr", self.careerPoints, self.agentPoints)

@Handlers.Handle(XT.BuyEpfItem)
def handleBuyEpfItem(self, data):
    if self.server.items.isItemEPF(data.ItemId):
        if data.ItemId not in self.server.items:
            return self.sendError(402)

        elif data.ItemId in self.inventory:
            return self.sendError(400)

        itemCost = self.server.items.getCost(data.ItemId)

        if self.agentPoints < itemCost:
            return self.sendError(401)

        self.inventory.append(data.ItemId)

        stringifiedInventory = map(str, self.inventory)
        self.user.Inventory = "%".join(stringifiedInventory)

        self.agentPoints -= itemCost

        self.user.EPF = ",".join(map(str, [self.agentStatus, self.fieldOpStatus,
                                       self.careerPoints, self.agentPoints]))
        self.session.commit()
        self.sendXt("epfai", self.agentPoints)
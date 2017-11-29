from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.UpdateColor)
@Handlers.Throttle(1)
def handleSendUpdatePlayerColour(self, data):
    if data.ItemId in self.inventory and self.server.items.isItemColor(data.ItemId):
        self.user.Color = data.ItemId
        self.room.sendXt("upc", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHead)
@Handlers.Throttle(1)
def handleSendUpdatePlayerHead(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemHead(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Head = data.ItemId
        self.room.sendXt("uph", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFace)
@Handlers.Throttle(1)
def handleSendUpdatePlayerFace(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemFace(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Face = data.ItemId
        self.room.sendXt("upf", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateNeck)
@Handlers.Throttle(1)
def handleSendUpdatePlayerNeck(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemNeck(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Neck = data.ItemId
        self.room.sendXt("upn", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateBody)
@Handlers.Throttle(1)
def handleSendUpdatePlayerBody(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemBody(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Body = data.ItemId
        self.room.sendXt("upb", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHand)
@Handlers.Throttle(1)
def handleSendUpdatePlayerHand(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemHand(data.ItemId)) \
            or data.ItemId == 0 or self.server.items.isPuffle(data.ItemId):
        self.user.Hand = data.ItemId
        self.room.sendXt("upa", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFeet)
@Handlers.Throttle(1)
def handleSendUpdatePlayerFeet(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemFeet(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Feet = data.ItemId
        self.room.sendXt("upe", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFlag)
@Handlers.Throttle(1)
def handleSendUpdatePlayerFlag(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemPin(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Feet = data.ItemId
        self.room.sendXt("upl", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdatePhoto)
@Handlers.Throttle(1)
def handleSendUpdatePlayerPhoto(self, data):
    if (data.ItemId in self.inventory and self.server.items.isItemPhoto(data.ItemId)) \
            or data.ItemId == 0:
        self.user.Photo = data.ItemId
        self.room.sendXt("upp", self.user.ID, data.ItemId)
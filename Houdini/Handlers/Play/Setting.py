from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.UpdateColor)
def handleSendUpdatePlayerColour(self, data):
    if data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 1:
        self.user.Color = data.ItemId
        self.room.sendXt("upc", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHead)
def handleSendUpdatePlayerHead(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 2) \
            or data.ItemId == 0:
        self.user.Head = data.ItemId
        self.room.sendXt("uph", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFace)
def handleSendUpdatePlayerFace(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 3) \
            or data.ItemId == 0:
        self.user.Face = data.ItemId
        self.room.sendXt("upf", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateNeck)
def handleSendUpdatePlayerNeck(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 4) \
            or data.ItemId == 0:
        self.user.Neck = data.ItemId
        self.room.sendXt("upn", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateBody)
def handleSendUpdatePlayerBody(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 5) \
            or data.ItemId == 0:
        self.user.Body = data.ItemId
        self.room.sendXt("upb", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHand)
def handleSendUpdatePlayerHand(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 6) \
            or data.ItemId == 0:
        self.user.Hand = data.ItemId
        self.room.sendXt("upa", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFeet)
def handleSendUpdatePlayerFeet(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 7) \
            or data.ItemId == 0:
        self.user.Feet = data.ItemId
        self.room.sendXt("upe", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFlag)
def handleSendUpdatePlayerFlag(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 8) \
            or data.ItemId == 0:
        self.user.Feet = data.ItemId
        self.room.sendXt("upl", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdatePhoto)
def handleSendUpdatePlayerPhoto(self, data):
    if (data.ItemId in self.inventory and self.server.items[data.ItemId]["type"] == 9) \
            or data.ItemId == 0:
        self.user.Photo = data.ItemId
        self.room.sendXt("upp", self.user.ID, data.ItemId)
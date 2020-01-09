from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.UpdateColor)
@Handlers.Throttle()
def handleSendUpdatePlayerColour(self, data):
    if data.ItemId in self.inventory and self.server.items.isItemColor(data.ItemId):
        self.user.Color = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upc", self.user.ID, data.ItemId)
        else:
            self.sendXt("upc", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHead)
@Handlers.Throttle()
def handleSendUpdatePlayerHead(self, data):
    if data.ItemId == 0 or(data.ItemId in self.inventory and self.server.items.isItemHead(data.ItemId)):
        self.user.Head = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("uph", self.user.ID, data.ItemId)
        else:
            self.sendXt("uph", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFace)
@Handlers.Throttle()
def handleSendUpdatePlayerFace(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemFace(data.ItemId)):
        self.user.Face = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upf", self.user.ID, data.ItemId)
        else:
            self.sendXt("upf", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateNeck)
@Handlers.Throttle()
def handleSendUpdatePlayerNeck(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemNeck(data.ItemId)):
        self.user.Neck = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upn", self.user.ID, data.ItemId)
        else:
            self.sendXt("upn", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateBody)
@Handlers.Throttle()
def handleSendUpdatePlayerBody(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemBody(data.ItemId)):
        self.user.Body = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upb", self.user.ID, data.ItemId)
        else:
            self.sendXt("upb", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHand)
@Handlers.Throttle()
def handleSendUpdatePlayerHand(self, data):
    if data.ItemId == 0 or self.server.items.isPuffle(data.ItemId) or \
            (data.ItemId in self.inventory and self.server.items.isItemHand(data.ItemId)):
        self.user.Hand = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upa", self.user.ID, data.ItemId)
        else:
            self.sendXt("upa", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFeet)
@Handlers.Throttle()
def handleSendUpdatePlayerFeet(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemFeet(data.ItemId)):
        self.user.Feet = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upe", self.user.ID, data.ItemId)
        else:
            self.sendXt("upe", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFlag)
@Handlers.Throttle()
def handleSendUpdatePlayerFlag(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemPin(data.ItemId)):
        self.user.Flag = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upl", self.user.ID, data.ItemId)
        else:
            self.sendXt("upl", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdatePhoto)
@Handlers.Throttle()
def handleSendUpdatePlayerPhoto(self, data):
    if data.ItemId == 0 or (data.ItemId in self.inventory and self.server.items.isItemPhoto(data.ItemId)):
        self.user.Photo = data.ItemId
        if self.user.Moderator != 2:
            self.room.sendXt("upp", self.user.ID, data.ItemId)
        else:
            self.sendXt("upp", self.user.ID, data.ItemId)

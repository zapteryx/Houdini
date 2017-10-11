from Houdini.Handlers import Handlers, XT

@Handlers.Handle(XT.UpdateColor)
def handleSendUpdatePlayerColour(self, data):
    self.user.Color = data.ItemId
    self.room.sendXt("upc", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHead)
def handleSendUpdatePlayerHead(self, data):
    self.user.Head = data.ItemId
    self.room.sendXt("uph", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFace)
def handleSendUpdatePlayerFace(self, data):
    self.user.Face = data.ItemId
    self.room.sendXt("upf", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateNeck)
def handleSendUpdatePlayerNeck(self, data):
    self.user.Neck = data.ItemId
    self.room.sendXt("upn", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateBody)
def handleSendUpdatePlayerBody(self, data):
    self.user.Body = data.ItemId
    self.room.sendXt("upb", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateHand)
def handleSendUpdatePlayerHand(self, data):
    self.user.Hand = data.ItemId
    self.room.sendXt("upa", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFeet)
def handleSendUpdatePlayerFeet(self, data):
    self.user.Feet = data.ItemId
    self.room.sendXt("upe", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdateFlag)
def handleSendUpdatePlayerFlag(self, data):
    self.user.Feet = data.ItemId
    self.room.sendXt("upl", self.user.ID, data.ItemId)

@Handlers.Handle(XT.UpdatePhoto)
def handleSendUpdatePlayerPhoto(self, data):
    self.user.Photo = data.ItemId
    self.room.sendXt("upp", self.user.ID, data.ItemId)
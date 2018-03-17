from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Item(SchemaObject):
    pass

class ItemSchema(Schema):
    Id = fields.Integer(load_from="paper_item_id")
    Type = fields.Integer(load_from="type")
    Cost = fields.Integer(load_from="cost")
    Member = fields.Boolean(load_from="is_member")
    Name = fields.String(load_from="label")
    Prompt = fields.String(load_from="prompt")
    Layer = fields.Integer(load_from="layer")
    Bait = fields.Boolean(load_from="is_bait", required=False)
    EPF = fields.Boolean(load_from="is_epf", required=False)
    Tour = fields.Boolean(load_from="make_tour_guide", required=False)

    @post_load
    def make_item(self, data):
        return Item(**data)

class ItemCollection(SchemaObjectCollection):

    def isItemColor(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 1

    def isItemHead(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 2

    def isItemFace(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 3

    def isItemNeck(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 4

    def isItemBody(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 5

    def isItemHand(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 6

    def isItemFeet(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 7

    def isItemPin(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 8

    def isItemPhoto(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 9

    def isItemAward(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 10

    def isBait(self, itemId):
        return hasattr(self.schemaObjects[int(itemId)], "Bait")

    def isItemEPF(self, itemId):
        return hasattr(self.schemaObjects[int(itemId)], "EPF")

    def isTourGuide(self, itemId):
        return hasattr(self.schemaObjects[int(itemId)], "Tour")

    def isPuffle(self, itemId):
        return itemId in range(750, 759)

    def getCost(self, itemId):
        return self.schemaObjects[int(itemId)].Cost

    def getItem(self, itemId):
        return self.schemaObjects[int(itemId)]
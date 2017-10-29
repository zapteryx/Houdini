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

    @post_load
    def make_item(self, data):
        return Item(**data)

class ItemCollection(SchemaObjectCollection):

    def isItemColor(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 1

    def isItemPin(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 8

    def isItemAward(self, itemId):
        return self.schemaObjects[int(itemId)].Type == 10

    def isBait(self, itemId):
        return hasattr(self.schemaObjects[int(itemId)], "Bait")

    def getCost(self, itemId):
        return self.schemaObjects[int(itemId)].Cost

    def getItem(self, itemId):
        return self.schemaObjects[int(itemId)]
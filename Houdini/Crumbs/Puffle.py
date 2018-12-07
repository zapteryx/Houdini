from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class CareItem(SchemaObject):
    pass

class CareItemEffect(SchemaObject):
    pass

class CareItemEffectSchema(Schema):
    Food = fields.Integer(load_from="food")
    Rest = fields.Integer(load_from="rest")
    Play = fields.Integer(load_from="play")
    Clean = fields.Integer(load_from="clean")

    @post_load
    def make_effect(self, data):
        return CareItemEffect(**data)

class CareItemSchema(Schema):
    Id = fields.Integer(load_from="puffle_item_id")
    Cost = fields.Integer(load_from="cost")
    Quantity = fields.Integer(load_from="quantity")
    Member = fields.Boolean(load_from="is_member_only")
    Name = fields.String(load_from="label")
    Prompt = fields.String(load_from="prompt")
    RootItemId = fields.Integer(load_from="root_item_id")
    Effect = fields.Nested(CareItemEffectSchema, load_from="effect")

    @post_load
    def make_item(self, data):
        return CareItem(**data)

class CareItemCollection(SchemaObjectCollection):

    def getQuantity(self, careItemId):
        return self.schemaObjects[careItemId].Quantity

    def getRootItem(self, careItemId):
        return self.schemaObjects[careItemId].RootItemId

    def getCost(self, careItemId):
        return self.schemaObjects[careItemId].Cost

    def getItem(self, careItemId):
        return self.schemaObjects[careItemId]

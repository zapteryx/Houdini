from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Igloo(SchemaObject):
    pass

class IglooSchema(Schema):
    Id = fields.Integer(load_from="igloo_id")
    Cost = fields.Integer(load_from="cost")
    Name = fields.String(load_from="label")
    Bait = fields.String(load_from="is_bait", required=False)

    @post_load
    def make_igloo(self, data):
        return Igloo(**data)

class IglooCollection(SchemaObjectCollection):

    def isBait(self, iglooId):
        return hasattr(self.schemaObjects[int(iglooId)], "Bait")

    def getCost(self, iglooId):
        return self.schemaObjects[iglooId].Cost

    def getItem(self, iglooId):
        return self.schemaObjects[iglooId]

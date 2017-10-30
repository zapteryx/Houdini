from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Igloo(SchemaObject):
    pass

class IglooSchema(Schema):
    Id = fields.Integer(load_from="igloo_id")
    Cost = fields.Integer(load_from="cost")
    Name = fields.String(load_from="label")

    @post_load
    def make_igloo(self, data):
        return Igloo(**data)

class IglooCollection(SchemaObjectCollection):

    def getCost(self, iglooId):
        return self.schemaObjects[iglooId].Cost

    def getItem(self, iglooId):
        return self.schemaObjects[iglooId]

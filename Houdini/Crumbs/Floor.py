from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Floor(SchemaObject):
    pass

class FloorSchema(Schema):
    Id = fields.Integer(load_from="igloo_floor_id")
    Cost = fields.Integer(load_from="cost")
    Name = fields.String(load_from="label")
    Prompt = fields.String(load_from="prompt")
    Bait = fields.String(load_from="is_bait", required=False)

    @post_load
    def make_floor(self, data):
        return Floor(**data)

class FloorCollection(SchemaObjectCollection):

    def isBait(self, floorId):
        return hasattr(self.schemaObjects[int(floorId)], "Bait")

    def getCost(self, floorId):
        return self.schemaObjects[floorId].Cost

    def getItem(self, floorId):
        return self.schemaObjects[floorId]

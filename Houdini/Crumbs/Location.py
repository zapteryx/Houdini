from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Location(SchemaObject):
    pass

class LocationSchema(Schema):
    Id = fields.Integer(load_from="igloo_location_id")
    Cost = fields.Integer(load_from="cost")
    Name = fields.String(load_from="label")
    Bait = fields.String(load_from="is_bait", required=False)

    @post_load
    def make_location(self, data):
        return Location(**data)

class LocationCollection(SchemaObjectCollection):

    def isBait(self, locationId):
        return hasattr(self.schemaObjects[int(locationId)], "Bait")

    def getCost(self, locationId):
        return self.schemaObjects[locationId].Cost

    def getItem(self, locationId):
        return self.schemaObjects[locationId]

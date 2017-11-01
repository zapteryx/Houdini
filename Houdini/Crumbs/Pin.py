import time

from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Pin(SchemaObject):
    pass

class PinSchema(Schema):
    Id = fields.Integer(load_from="paper_item_id")
    Unix = fields.Integer(load_from="unix")
    Label = fields.String(load_from="label")
    ReleaseDate = fields.String(load_from="release_date")
    Location = fields.String(load_from="location")

    @post_load
    def make_pin(self, data):
        return Pin(**data)

class PinCollection(SchemaObjectCollection):

    def getUnixTimestamp(self, pinId):
        return self.schemaObjects[int(pinId)].Unix \
            if int(pinId) in self.schemaObjects else int(time.time())

    def getPin(self, pinId):
        return self.schemaObjects[int(pinId)]
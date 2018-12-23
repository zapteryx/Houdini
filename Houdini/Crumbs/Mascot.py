from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Mascot(SchemaObject):
    def __init__(self, **data):
        super(Mascot, self).__init__(**data)

class MascotSchema(Schema):
    Id = fields.Integer(load_from="mascot_id")
    InternalId = fields.Integer(required=False)

    @post_load
    def make_mascot(self, data):
        return Mascot(**data)

class MascotCollection(SchemaObjectCollection):

    def __init__(self, deserializedMascotObjects):
        super(MascotCollection, self).__init__(deserializedMascotObjects)

        # Set internal ID
        internalId = 1

        for mascotId, mascotObject in self.schemaObjects.items():
            mascotObject.InternalId = internalId
            internalId += 1

    def getMascot(self, mascotId):
        return self.schemaObjects[int(mascotId)]

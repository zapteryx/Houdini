from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

GameGroupIds = {
    13: ("Aqua Grabber", 916),
    14: ("Astro Barrier", 900),
    38: ("Card-Jitsu", 998),
    32: ("Card-Jitsu : Fire", 997),
    34: ("Card-Jitsu : Water", 995),
    28: ("Cart Surfer", 905),
    15: ("Catchin' Waves", 912),
    11: ("Jet Pack Adventure", 906),
    22: ("Missions", 907, 908, 911, 913, 914, 915, 920, 921, 922, 923, 927)
}

class Stamp(SchemaObject):
    pass

class StampGroup(SchemaObject):
    pass

class StampSchema(Schema):
    Id = fields.Integer(load_from="stamp_id")
    Name = fields.String(load_from="name")
    IsMember = fields.Boolean(load_from="is_member")
    Rank = fields.Integer(load_from="rank")
    Description = fields.String(load_from="description")
    RankToken = fields.String(load_from="rank_token")

    @post_load()
    def make_stamp(self, data):
        return Stamp(**data)

class StampGroupSchema(Schema):
    Id = fields.Integer(load_from="group_id")
    ParentGroupId = fields.Integer(load_from="parent_group_id")
    Name = fields.String(load_from="name")
    Description = fields.String(load_from="description")
    Display = fields.String(load_from="display")
    Stamps = fields.List(fields.Nested(StampSchema()), load_from="stamps")
    RoomIds = fields.List(fields.Integer(), required=False)

    @post_load()
    def make_group(self, data):
        return StampGroup(**data)

class StampGroupCollection(SchemaObjectCollection):

    def __init__(self, deserializedStampGroupObjects):
        super(StampGroupCollection, self).__init__(deserializedStampGroupObjects)

        self.stampsById = {}
        self.stampGroupByRoomId = {}

        for stampGroupId, stampGroupObject in self.schemaObjects.items():
            stampGroupObject.StampsById = {}
            for stampObject in stampGroupObject.Stamps:
                stampObject.StampGroup = stampGroupObject
                self.stampsById[stampObject.Id] = stampObject

                if stampGroupId not in GameGroupIds:
                    continue

                for roomId in GameGroupIds[stampGroupId][1:]:
                    self.stampGroupByRoomId[roomId] = stampGroupObject
                    stampGroupObject.RoomIds = GameGroupIds[stampGroupId][1:]

                stampGroupObject.StampsById[stampObject.Id] = stampObject

    def getStampGroup(self, stampGroupId):
        return self.schemaObjects[stampGroupId]

    def getStampGroupByRoomId(self, roomId):
        return self.stampGroupByRoomId[roomId]

    def isStampRoom(self, roomId):
        return roomId in self.stampGroupByRoomId

class StampCollection(SchemaObjectCollection):

    def getStamp(self, stampId):
        return self.schemaObjects[stampId]

StampSchema.StampGroup = fields.Nested(StampGroupSchema(), required=False)
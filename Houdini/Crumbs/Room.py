from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Room(SchemaObject):

    def __init__(self, **data):
        super(Room, self).__init__(**data)

        self.players = []

    def send(self, data):
        for player in self.players:
            player.sendLine(data)

    def sendXt(self, *data):
        for player in self.players:
            player.sendXt(*data)

    def generateRoomString(self):
        roomString = "%".join([player.getPlayerString() for player in self.players])

        return roomString

    def add(self, player):
        self.players.append(player)

        player.room = self
        player.frame = 1

        if 900 <= self.Id <= 1000:
            player.sendXt("jg", self.Id)
        else:
            player.sendXt("jr", self.Id, self.generateRoomString())

        self.sendXt("ap", player.getPlayerString())

    def refresh(self, player):
        player.sendXt("grs", self.Id, self.generateRoomString())

    def remove(self, player):
        self.players.remove(player)

        self.sendXt("rp", player.user.ID)


class RoomSchema(Schema):
    Id = fields.Integer(load_from="room_id")
    InternalId = fields.Integer(required=False)
    Key = fields.String(load_from="room_key")
    Name = fields.String(load_from="name")
    DisplayName = fields.String(load_from="display_name")
    MusicId = fields.Integer(load_from="music_id")
    Member = fields.Integer(load_from="is_member")
    Path = fields.String(load_from="path")
    MaxUsers = fields.Integer(load_from="max_users")
    JumpEnabled = fields.Boolean(load_from="jump_enabled")
    JumpDisabled = fields.Boolean(load_from="jump_disabled")
    RequiredItem = fields.Integer(load_from="required_item", allow_none=True)
    ShortName = fields.String(load_from="short_name")

    @post_load
    def make_room(self, data):
        return Room(**data)

class RoomCollection(SchemaObjectCollection):

    def __init__(self, deserializedRoomObjects):
        super(RoomCollection, self).__init__(deserializedRoomObjects)

        # Set internal ID
        internalId = 1

        for roomId, roomObject in self.schemaObjects.items():
            roomObject.InternalId = internalId
            internalId += 1

    def isRoomFull(self, roomId):
        pass

    def isRoomIgloo(self, roomId):
        pass
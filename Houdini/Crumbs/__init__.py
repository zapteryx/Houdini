import os, json, logging

logger = logging.getLogger("Houdini")

class SchemaObject(object):
    def __init__(self, **fieldKeywords):
        for fieldKey, fieldValue in fieldKeywords.items():
            setattr(self, fieldKey, fieldValue)

    def __repr__(self):
        return '<{}(name={self.Name!r})>'.format(self.__class__.__name__, self=self)

class SchemaObjectCollection(object):

    def __init__(self, deserializedResults):
        super(SchemaObjectCollection, self).__init__()

        self.schemaObjects = {}

        for deserializedObject in deserializedResults:
            self.schemaObjects[deserializedObject.Id] = deserializedObject

    def __getitem__(self, objectId):
        if objectId not in self.schemaObjects:
            raise KeyError("Object id (%d) not in %s." % (objectId, self.__class__.__name__))

        return self.schemaObjects[objectId]

    def __setitem__(self, objectId, objectInstance):
        self.schemaObjects[objectId] = objectInstance

    def __contains__(self, objectId):
        return objectId in self.schemaObjects

    def __len__(self):
        return len(self.schemaObjects)

from Houdini.Crumbs.Item import ItemSchema, ItemCollection
from Houdini.Crumbs.Room import RoomSchema, RoomCollection

def retrieveItemCollection(crumbsFile="crumbs/paper_items.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        items = json.load(fileHandle)

        schema = ItemSchema(many=True)
        result = schema.load(items)

        itemCollection = ItemCollection(result.data)

        logger.info("%d items loaded", len(itemCollection))

        return itemCollection

def retrieveRoomCollection(crumbsFile="crumbs/rooms.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as roomsFileHandle:
        rooms = json.load(roomsFileHandle)

        schema = RoomSchema(many=True)
        result = schema.load(rooms.values())

        roomCollection = RoomCollection(result.data)

        return roomCollection
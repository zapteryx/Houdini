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

    def __getattr__(self, item):
        if hasattr(self.schemaObjects, item):
            return getattr(self.schemaObjects, item)

        raise AttributeError("%s doesn't exist in %s." % self.__class__.__name__)

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
from Houdini.Crumbs.Furniture import FurnitureSchema, FurnitureCollection
from Houdini.Crumbs.Floor import FloorSchema, FloorCollection
from Houdini.Crumbs.Igloo import IglooSchema, IglooCollection
from Houdini.Crumbs.Pin import PinSchema, PinCollection
from Houdini.Crumbs.Stamp import StampSchema, StampGroupSchema,\
    StampGroupCollection, StampCollection
from Houdini.Crumbs.Card import CardSchema, CardCollection
from Houdini.Crumbs.Dance import SongSchema, DanceCollection

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

def retrieveFurnitureCollection(crumbsFile="crumbs/furniture_items.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        furniture = json.load(fileHandle)

        schema = FurnitureSchema(many=True)
        result = schema.load(furniture)

        furnitureCollection = FurnitureCollection(result.data)

        logger.info("%d furniture items loaded", len(furnitureCollection))

        return furnitureCollection

def retrieveFloorCollection(crumbsFile="crumbs/igloo_floors.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        flooring = json.load(fileHandle)

        schema = FloorSchema(many=True)
        result = schema.load(flooring)

        floorCollection = FloorCollection(result.data)

        logger.info("%d floor items loaded", len(floorCollection))

        return floorCollection

def retrieveIglooCollection(crumbsFile="crumbs/igloos.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        igloos = json.load(fileHandle)

        schema = IglooSchema(many=True)
        result = schema.load(igloos.values())

        iglooCollection = IglooCollection(result.data)

        logger.info("%d igloo items loaded", len(iglooCollection))

        return iglooCollection

def retrievePinCollection(crumbsFile="crumbs/pins.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        pins = json.load(fileHandle)

        schema = PinSchema(many=True)
        result = schema.load(pins)

        pinCollection = PinCollection(result.data)

        logger.info("%d pins loaded", len(pinCollection))

        return pinCollection

def retrieveStampsCollection(crumbsFile="crumbs/stamps.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        stamps = json.load(fileHandle)

        schema = StampGroupSchema(many=True)
        result = schema.load(stamps)

        stampGroupCollection = StampGroupCollection(result.data)

        stampCollection = StampCollection(stampGroupCollection.stampsById.values())

        logger.info("%d stamps loaded", len(stampCollection))

        return stampGroupCollection, stampCollection

def retrieveCardCollection(crumbsFile="crumbs/cards.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        items = json.load(fileHandle)

        schema = CardSchema(many=True)
        result = schema.load(items)

        cardCollection = CardCollection(result.data)

        logger.info("%d cards loaded", len(cardCollection))

        return cardCollection

def retrieveDanceCollection(crumbsFile="crumbs/dance.json"):
    assert os.path.exists(crumbsFile), "%r does not exist" % crumbsFile

    with open(crumbsFile, "r") as fileHandle:
        dance = json.load(fileHandle)

        schema = SongSchema(many=True)
        result = schema.load(dance)

        danceCollection = DanceCollection(result.data)

        logger.info("%d dance tracks loaded", len(danceCollection))

        return danceCollection
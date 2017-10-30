from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Furniture(SchemaObject):
    pass

class FurnitureSchema(Schema):
    Id = fields.Integer(load_from="furniture_item_id")
    Type = fields.Integer(load_from="type")
    Cost = fields.Integer(load_from="cost")
    Member = fields.Boolean(load_from="is_member_only")
    Name = fields.String(load_from="label")
    Prompt = fields.String(load_from="prompt")
    MaxQuantity = fields.Integer(load_from="max_quantity")
    Sort = fields.Integer(load_from="sort")

    @post_load
    def make_furniture(self, data):
        return Furniture(**data)

class FurnitureCollection(SchemaObjectCollection):

    def getCost(self, furnitureId):
        return self.schemaObjects[furnitureId].Cost

    def getItem(self, furnitureId):
        return self.schemaObjects[furnitureId]

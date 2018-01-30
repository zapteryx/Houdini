from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Card(SchemaObject):

    def getString(self):
        return "|".join(map(str, [self.Id, self.Element, self.Value, self.Color, self.PowerId]))

class CardSchema(Schema):
    Id = fields.Integer(load_from="card_id")
    SetId = fields.Integer(load_from="set_id")
    PowerId = fields.Integer(load_from="power_id")
    Element = fields.String(load_from="element")
    Name = fields.String(load_from="name")
    Label = fields.String(load_from="label")
    Prompt = fields.String(load_from="prompt")
    Color = fields.String(load_from="color")
    Value = fields.Integer(load_from="value")
    Asset = fields.String(load_from="asset")
    Description = fields.String(load_from="description")
    Active = fields.Boolean(load_from="is_active")

    @post_load
    def make_card(self, data):
        return Card(**data)

class CardCollection(SchemaObjectCollection):
    pass
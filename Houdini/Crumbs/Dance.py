from marshmallow import Schema, fields, post_load
from Houdini.Crumbs import SchemaObject, SchemaObjectCollection

class Song(SchemaObject):
    pass

class Track(SchemaObject):
    pass

class TrackSchema(Schema):
    NoteTypes = fields.List(fields.Integer(), load_from="note_types")
    NoteTimes = fields.List(fields.Integer(), load_from="note_times")
    NoteLengths = fields.List(fields.Integer(), load_from="note_lengths")

    @post_load
    def make_track(self, data):
        return Track(**data)

class SongSchema(Schema):
    Id = fields.Integer(load_from="song_id")
    Name = fields.String(load_from="name")
    Length = fields.Integer(load_from="song_length")
    MillisPerBar = fields.Integer(load_from="millis_per_bar")
    TrackEasy = fields.Nested(TrackSchema, load_from="easy")
    TrackMedium = fields.Nested(TrackSchema, load_from="medium")
    TrackHard = fields.Nested(TrackSchema, load_from="hard")

    @post_load
    def make_song(self, data):
        return Song(**data)

class DanceCollection(SchemaObjectCollection):
    pass
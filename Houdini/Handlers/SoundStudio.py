from sqlalchemy import and_, or_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Penguin import Penguin
from Houdini.Data.SoundStudio import Musics
from Houdini.Handlers.Play.Player import getPlayerInfo, getPlayerSafeName
from Houdini.Handlers.Play.Moderation import cheatBan

@Handlers.Handle(XT.GetMyMusicTracks)
def handleGetMyMusicTracks(self, data):
    tracks = self.session.query(Musics).filter(and_(Musics.PenguinID == self.user.ID, Musics.Deleted == 0))
    musicTracks = ""
    if tracks.count() >0:
        for track in tracks:
            musicTracks = musicTracks + "{}|{}|{}|{},".format(track.ID, track.Name,track.Sharing, track.Likes)

        musicTracks = musicTracks[:-1]
    self.sendXt("getmymusictracks", tracks.count(), musicTracks)

@Handlers.Handle(XT.RefreshTrackLikes)
def handleRefreshTrackLikes(self, data):
    tracks = self.session.query(Musics).filter(and_(Musics.PenguinID == self.user.ID, Musics.Deleted == 0))
    if tracks.count() >0:
        for track in tracks:
            self.sendXt("getlikecountfortrack", self.user.ID, track.ID, track.Likes)

@Handlers.Handle(XT.DeleteTrack)
def handleDeleteTrack(self, data):
    tracks = self.session.query(Musics).filter(and_(Musics.PenguinID == self.user.ID, Musics.Deleted == 0, Musics.ID == data.TrackId))
    if tracks.count() == 1:
        tracks.update({"Deleted": 1, "Sharing":0})
        self.sendXt('deletetrack%-1%1%')
    else:
        return self.transport.loseConnection()

@Handlers.Handle(XT.SaveMyMusicTrack)
def handleSaveMyMusicTrack(self, data):
        addmusic = Musics(PenguinID=self.user.ID, Name=data.Name, Data=data.Musica, Hash = data.Hash, Deleted = 0, Likes = 0)
        self.session.add(addmusic)
        idmusic = addmusic.ID
        self.session.commit()
        self.sendXt('savemymusictrack', -1, idmusic)

@Handlers.Handle(XT.ShareMyMusicTrack)
def handleShareMyMusicTrack(self, data):
    tracks = self.session.query(Musics).filter(and_(Musics.PenguinID == self.user.ID, Musics.Deleted == 0, Musics.ID == data.TrackId))
    if tracks.count() == 1:
        tracks.update({"Sharing": data.ValueShare})
        if data.ValueShare ==1:
            outros = self.session.query(Musics).filter(and_(Musics.PenguinID == self.user.ID, Musics.Deleted == 0, Musics.ID != data.TrackId))
            outros.update({"Sharing": 0})
        self.sendXt("sharemymusictrack%-1%1%")
    else:
        return self.transport.loseConnection()

@Handlers.Handle(XT.LoadMusicTrack)
def handleLoadMusicTrack(self, data):
    track = self.session.query(Musics).filter(and_(Musics.PenguinID == data.PengID, Musics.Deleted == 0, Musics.ID == data.TrackId))
    if track.count() == 1:
        for tracks in track:
            self.sendXt('loadmusictrack', tracks.ID, tracks.Name,tracks.Sharing, tracks.Data, tracks.Hash, tracks.Likes)
    else:
        return self.transport.loseConnection()

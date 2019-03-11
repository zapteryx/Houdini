import random, time

from twisted.internet import reactor

from Houdini.Handlers import Handlers, XT

class DanceFloor(object):

    def __init__(self, songs):
        self.queue = []
        self.penguins = []
        self.scores = {}
        self.songs = songs
        self.currentSong = None
        self.nextSongTime = 0
        self.nextSongId = 1
        self.changeSong()

    def add(self, penguin):
        if penguin not in self.penguins and penguin not in self.queue:
            self.queue.append(penguin)
            self.scores[penguin] = "0"

    def remove(self, penguin):
        if penguin in self.penguins:
            self.penguins.remove(penguin)
        elif penguin in self.queue:
            self.queue.remove(penguin)

    def changeSong(self):
        self.sendXt("zf", self.getString())
        self.penguins = []
        self.currentSong = self.songs[self.nextSongId]
        self.nextSongId = random.randrange(0, 6)

        self.nextSongTime = int(round(time.time() * 1000)) + self.currentSong.Length

        for penguin in self.queue:
            self.penguins.append(penguin)
        self.queue = []

        trackDifficulties = [self.currentSong.TrackEasy, self.currentSong.TrackMedium,
                             self.currentSong.TrackHard, self.currentSong.TrackHard]

        for penguin in self.penguins:
            track = trackDifficulties[penguin.difficulty]
            penguin.sendXt("sz", ",".join(map(str, track.NoteTimes)), ",".join(map(str, track.NoteTypes)),
                           ",".join(map(str, track.NoteLengths)), self.currentSong.MillisPerBar)

        self.sendXt("zm", self.getString())

        reactor.callLater(self.currentSong.Length / 1000, self.changeSong)

    def getString(self):
        string = []
        for penguin in self.penguins:
            string.append("|".join(["-1", penguin.user.SafeName, self.scores[penguin]]))
        return ",".join(string)

    def getTimeToNextSong(self):
        return self.nextSongTime - int(round(time.time() * 1000))

    def sendXt(self, *data):
        for penguin in self.penguins:
            penguin.sendXt(*data)

@Handlers.Handle(XT.GetGame)
@Handlers.Handle(XT.GetGameAgain)
def handleGetGame(self, data):
    if self.room.Id == 952:
        if len(self.server.danceFloor.queue) < 15:
            self.server.danceFloor.add(self)
            self.sendXt("gz", 0, self.server.danceFloor.nextSongId, self.server.danceFloor.getTimeToNextSong())
            self.sendXt("jz", "true", self.server.danceFloor.nextSongId, self.server.danceFloor.getTimeToNextSong())
        else:
            self.sendXt("jz", "false")

@Handlers.Handle(XT.ChangeDifficulty)
def handleChangeDifficulty(self, data):
    if self.room.Id == 952:
        self.difficulty = data.Difficulty

@Handlers.Handle(XT.SendMove)
def handleSendMove(self, data):
    if self in self.server.danceFloor.penguins:
        score = data.Move[0]
        self.server.danceFloor.scores[self] = score
        self.server.danceFloor.sendXt("zm", self.server.danceFloor.getString())

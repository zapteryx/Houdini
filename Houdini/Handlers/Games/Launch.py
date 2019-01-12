from sqlalchemy import and_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.GameData import GameDataLaunch

from canon import Compressor
from canon.data.launch import load_data_set_from_object, load_data_set_into_object

@Handlers.Handle(XT.GetGameData)
def handleGetGameData(self, data):
    gameData = self.session.query(GameDataLaunch).filter(GameDataLaunch.PenguinID == self.user.ID).all()
    data = {}
    for level in gameData:
        levelId = level.LevelID
        data[levelId] = {}
        data[levelId]["PuffleOs"] = level.PuffleOs
        data[levelId]["BestTime"] = level.BestTime
        data[levelId]["TurboDone"] = True if level.TurboDone == 1 else False

    new_data_set = load_data_set_from_object(data)
    compressed = Compressor.compress(new_data_set)
    savedata = compressed.encode('utf-8')

    self.sendXt("ggd", savedata)

@Handlers.Handle(XT.SaveGameData)
def handleSaveGameData(self, data):
    savedata = data.Data[0].decode("utf-8")
    decompressed = Compressor.decompress(savedata)
    decompressed_data = load_data_set_into_object(decompressed, filtered=True)

    for level in decompressed_data:
        puffleOs = decompressed_data[level]["PuffleOs"]
        bestTime = decompressed_data[level]["BestTime"]
        turboDone = decompressed_data[level]["TurboDone"]

        turboDone = 1 if turboDone == True else 0

        levelsPlayed = self.session.query(GameDataLaunch).filter(and_(GameDataLaunch.PenguinID == self.user.ID, GameDataLaunch.LevelID == level)).scalar()
        if not levelsPlayed:
            self.session.add(GameDataLaunch(PenguinID=self.user.ID, LevelID=level, PuffleOs=puffleOs, BestTime=bestTime, TurboDone=turboDone))
        else:
            self.session.query(GameDataLaunch).filter(and_(GameDataLaunch.PenguinID == self.user.ID,GameDataLaunch.LevelID == level)) \
                        .update({"PuffleOs": puffleOs,"BestTime": bestTime, "TurboDone": turboDone})

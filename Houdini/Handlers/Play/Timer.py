import logging, threading

from Houdini.Handlers import Handlers, XT
from Houdini.Events import Events
from Houdini.Data.Timer import Timer

from datetime import datetime, timedelta

def updateEggTimer(self, timeLeft, totalDailyTime):
    self.minutesToday = totalDailyTime - timeLeft
    self.minutesToday += 1
    timeLeft -= 1

    self.eggTimer = threading.Timer(60.0, updateEggTimer, [self, timeLeft, totalDailyTime])
    self.eggTimer.start()

    if timeLeft == 7 or timeLeft == 1 or timeLeft == 0:
        dailyHours = int(totalDailyTime / 60)
        dailyMins = totalDailyTime - (dailyHours * 60)
        total = str(dailyHours) + ":" + str(dailyMins)
        self.sendXt("uet", timeLeft)
        if timeLeft == 0:
            self.sendXt("e", "910", total)
            self.transport.loseConnection()
        else:
            self.sendXt("e", "914", timeLeft, total)
    else:
        self.sendXt("uet", timeLeft)

def checkHours(self, oldStartHours, oldEndHours, first=0):
    self.session.commit()
    timer = self.session.query(Timer).filter(Timer.PenguinID == self.user.ID).first()
    startHours = timer.PlayHourStart
    endHours = timer.PlayHourEnd
    offset = timer.UTCOffset

    if first == 1:
        today = datetime.today()
        if today.minute+1 == 59:
            nextMinute = 0
        else:
            nextMinute = today.minute+1
        everyMin = today.replace(minute=nextMinute, second=0, microsecond=0)
        deltaEveryMin = everyMin - today
        self.timerSecs = deltaEveryMin.seconds+1
        self.hourTimer = threading.Timer(self.timerSecs, checkHours, [self, startHours, endHours])
    else:
        self.hourTimer = threading.Timer(60.0, checkHours, [self, startHours, endHours])

    self.hourTimer.start()

    start = datetime.strptime(str(startHours), "%H:%M:%S")
    end = datetime.strptime(str(endHours), "%H:%M:%S")
    now = datetime.utcnow().strftime("%H:%M:%S")
    now = datetime.strptime(str(now), "%H:%M:%S")

    diff = end - now
    hrs = str(diff).split(':')[0]
    mins = str(diff).split(':')[1]

    offsetStartHours = format(start + timedelta(hours=offset), "%H:%M:%S")
    offsetEndHours = format(end + timedelta(hours=offset), "%H:%M:%S")

    # When the player is nearly out of hours
    if (int(mins) == 7 and int(hrs) == 0) or (int(mins) == 1 and int(hrs) == 0):
        self.sendXt("e", "915", mins, offsetStartHours, offsetEndHours)
    elif int(mins) <= 0 and int(hrs) == 0:
        self.sendXt("e", "916", offsetStartHours, offsetEndHours) # error 916 disconnects the player for us so we don't need to

    # Check if the allowed hours have been changed whilst online
    if str(oldStartHours) != str(startHours) or str(oldEndHours) != str(endHours):
        if startHours >= datetime.utcnow().time() or endHours <= datetime.utcnow().time():
            self.sendXt("e", "917", offsetStartHours, offsetEndHours) # error 917 disconnects the player for us so we don't need to
        else:
            self.sendXt("e", "918", offsetStartHours, offsetEndHours)

def handleDisconnection(self):
    if hasattr(self, 'hourTimer'):
        self.hourTimer.cancel()
    if hasattr(self, 'eggTimer'):
        self.eggTimer.cancel()
    if hasattr(self, 'minutesToday'):
        self.session.query(Timer.MinutesToday).filter(Timer.PenguinID == self.user.ID).update({"MinutesToday": self.minutesToday})
        self.session.commit()

Events.Register("Disconnected", handleDisconnection)

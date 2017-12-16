import zope.interface, logging
from sqlalchemy import Column, Integer, text
from sqlalchemy.exc import OperationalError

from Houdini.Plugins import Plugin
from Houdini.Handlers import Handlers
from Houdini.Data.Penguin import Penguin

class Rank(object):
    zope.interface.implements(Plugin)

    author = "Houdini Team"
    version = 0.1
    description = "Adjusts the chevron(s) on membership badges to represent the user's rank."

    membershipDaysByRank = [180, 360, 540, 720, 750]

    def __init__(self, server):
        self.logger = logging.getLogger("Houdini")

        self.server = server

        Penguin.Rank = Column(Integer, nullable=False, server_default=text("'1'"))

        try:
            self.server.databaseEngine.execute("ALTER TABLE penguins add Rank TINYINT(1) DEFAULT 1;")

        except OperationalError as opError:
            if "Duplicate column name" not in opError.message:
                self.logger.warn(opError.message)

        Handlers.Login += self.adjustMembershipDays

    def adjustMembershipDays(self, player, data):
        playerRank = player.session.query(Penguin.Rank). \
            filter(Penguin.ID == player.user.ID).scalar() - 1

        if playerRank > 5:
            playerRank = 4

        player.membershipDays = self.membershipDaysByRank[playerRank]

    def ready(self):
        self.logger.info("Rank plugin is ready!")
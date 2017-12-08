import logging
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.exc import InvalidRequestError
from twisted.protocols.basic import LineOnlyReceiver

from Houdini.Handlers import Handlers
from Houdini.Events import Events

class Spheniscidae(LineOnlyReceiver, object):

    delimiter = "\x00"

    def __init__(self, session, server):
        self.logger = logging.getLogger("Houdini")

        self.session = session
        self.server = server

        # Defined once the client requests it (see handleRandomKey)
        self.randomKey = None

    """
    The login server relies on knowing all the buddies the player has
    and since the login server uses this class instead of the Penguin child class,
    it's placed here. :-)
    """
    def getBuddyList(self):
        buddiesArray = self.user.Buddies.split('%')
        self.buddies = {}

        for buddyDetails in buddiesArray:
            try:
                buddyId, buddyUsername = buddyDetails.split('|')
                self.buddies[int(buddyId)] = buddyUsername

            except ValueError as valueError:
                self.logger.debug('getBuddyList: %s', valueError.message)
                break  # No buddies

        return self.buddies

    def sendErrorAndDisconnect(self, error):
        self.sendError(error)
        self.transport.loseConnection()

    def sendError(self, error):
        self.sendXt("e", error)

    # TODO: Replace * with actual port
    def sendPolicyFile(self):
        self.sendLine("<cross-domain-policy><allow-access-from domain='*' to-ports='*' /></cross-domain-policy>")

    def handleXmlData(self, data):
        self.logger.debug("Received XML data: {0}".format(data))

        elementTree = ET.fromstring(data)

        if elementTree.tag == "policy-file-request":
            self.sendPolicyFile()

        elif elementTree.tag == "msg":
            self.logger.debug("Received valid XML data")

            try:
                bodyTag = elementTree[0]
                action = bodyTag.get("action")

                if Handlers.HandlerExists(action, "XML"):
                    Handlers.HandleXML(self, action, bodyTag)

                else:
                    self.logger.warn("Packet did not contain a valid action attribute!")

            except IndexError:
                self.logger.warn("Received invalid XML data (didn't contain a body tag)")
        else:
            self.logger.warn("Received invalid XML data!")


    def handleWorldData(self, data):
        self.logger.debug("Received XT data: {0}".format(data))

        # First and last elements are blank
        parsedData = data.split("%")[1:-1]

        packetId = parsedData[2]

        if Handlers.HandlerExists(packetId, "XT"):
            return Handlers.HandleXT(self, packetId, parsedData)


        self.logger.debug("Handler for {0} doesn't exist!".format(packetId))

    # TODO: Clean
    def sendXt(self, *data):
        data = list(data)

        handlerId = data.pop(0)

        try:
            internalId = self.room.internalId
        except AttributeError:
            internalId = -1

        mappedData = map(str, data)

        xtData = "%".join(mappedData)

        line = "%xt%{0}%{1}%{2}%".format(handlerId, internalId, xtData)
        self.sendLine(line)

    def sendXml(self, xmlDict):
        # Currently the root for all XML packets
        dataRoot = Element("msg")
        dataRoot.set("t", "sys")

        subElementParent = dataRoot
        for subElement, subElementAttribute in xmlDict.iteritems():
            subElementObject = SubElement(subElementParent, subElement)

            if type(xmlDict[subElement]) is dict:
                for subElementAttributeKey, subElementAttributeValue in xmlDict[subElement].iteritems():
                    subElementObject.set(subElementAttributeKey, subElementAttributeValue)
            else:
                subElementObject.text = xmlDict[subElement]

            subElementParent = subElementObject

        xmlData = tostring(dataRoot)
        self.sendLine(xmlData)

    def sendLine(self, line):
        super(Spheniscidae, self).sendLine(line)

        self.logger.debug("Outgoing data: {0}".format(line))

    def lineReceived(self, data):
        try:
            if data.startswith("<"):
                self.handleXmlData(data)
            else:
                self.handleWorldData(data)

        except UnicodeError as uniError:
            self.logger.error('Error decoding data')

    def connectionLost(self, reason):
        self.logger.info("Client disconnected")

        Events.Fire("Disconnected", self)

        try:
            self.session.commit()

            if hasattr(self, "user"):
                if self.user.ID in self.server.players:
                    del self.server.players[self.user.ID]

                self.session.expunge(self.user)

        except InvalidRequestError:
            self.logger.info("There aren't any transactions in progress")

        finally:
            self.session.close()

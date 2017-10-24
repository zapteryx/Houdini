class Room(object):

	def __init__(self, *room):
		self.externalId, self.internalId = room

		self.players = []

	def send(self, data):
		for player in self.players:
			player.sendLine(data)

	def sendXt(self, *data):
		for player in self.players:
			player.sendXt(*data)

	def generateRoomString(self):
		roomString = "%".join([player.getPlayerString() for player in self.players])

		return roomString

	def add(self, player):
		self.players.append(player)
		player.room = self
		player.frame = 1

		if 900 <= self.externalId <= 1000:
			player.sendXt("jg", self.externalId)
		else:
			player.sendXt("jr", self.externalId, self.generateRoomString())

		self.sendXt("ap", player.getPlayerString())

	def refresh(self, player):
		player.sendXt("grs", self.externalId, self.generateRoomString())

	def remove(self, player):
		self.players.remove(player)

		self.sendXt("rp", player.user.ID)

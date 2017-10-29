from Houdini.HoudiniFactory import HoudiniFactory

server = HoudiniFactory("houdini.conf", server="Wind")
server.start()
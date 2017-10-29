from Houdini.HoudiniFactory import HoudiniFactory

server = HoudiniFactory("houdini.conf", server="Login")
server.start()
from sqlalchemy import MetaData

from twisted.internet.defer import inlineCallbacks, returnValue

from alchimia.engine import TwistedEngine

metadata = MetaData()
def ResultProxyMethod(resultProxyMethod):
    @inlineCallbacks
    def actualMethod(engine, query, *args, **kwargs):
        methodName = resultProxyMethod.__name__
        result = yield engine.execute(query)
        record = yield getattr(result, methodName)(*args, **kwargs)
        returnValue(record)
    return actualMethod

class Engine(TwistedEngine):

    @ResultProxyMethod
    def first(self):
        raise NotImplementedError

    @ResultProxyMethod
    def fetchall(self):
        raise NotImplementedError

    @ResultProxyMethod
    def fetchmany(self):
        raise NotImplementedError

    @ResultProxyMethod
    def fetchone(self):
        raise NotImplementedError

    @ResultProxyMethod
    def scalar(self):
        raise NotImplementedError

wrap_engine = Engine.from_sqlalchemy_engine
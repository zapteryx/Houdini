from sqlalchemy import MetaData

from twisted.internet.defer import inlineCallbacks, returnValue

from alchimia.engine import TwistedEngine

metadata = MetaData()

class RowProxyDictionary(dict):

    def __init__(self, engine, *args, **kwargs):
        super(RowProxyDictionary, self).__init__(*args, **kwargs)
        dict.__setattr__(self, "engine", engine)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(RowProxyDictionary, self).__setitem__(key, value)
        self.__dict__.update({key: value})

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
import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError

Base = declarative_base()

def commitOrRollback(retries=5):
    def decoratorFunction(f):
        def retryFunction(callerObject, *args, **kwargs):
            handleTries = retries
            while handleTries > 0:
                try:
                    return f(callerObject, *args, **kwargs)
                except OperationalError as exception:
                    logger = logging.getLogger("Houdini")
                    if handleTries > 1:
                        logger.error("Caught operational error! Retrying ({})".format(exception.message))
                    else:
                        logger.error("Caught operational error! Giving up ({})".format(exception.message))
                        callerObject.session.rollback()
                    handleTries -= 1
            return f
        return retryFunction
    return decoratorFunction
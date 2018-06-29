import logging

from dogpile.cache import make_region

logging.basicConfig(level=logging.DEBUG)

def handlerKeyGenerator(namespace, fn):
    functionName = fn.__name__
    def generateKey(_, penguinId, *__):
        return namespace + "." + functionName + "." + str(penguinId)
    return generateKey

CacheRegion = make_region(
    function_key_generator=handlerKeyGenerator
)

Cache = CacheRegion.cache_on_arguments
from redis import Redis

from env import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT ,REDIS_FLUSH
from logger import logger


@logger.catch
def init_redis() -> Redis:
    r = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True, db=0)
    pong = r.ping()
    if not pong:
        raise ConnectionError(f"Redis connection failed: {pong}")
    logger.info("Init redis successfully")
    if REDIS_FLUSH:
        r.flushdb()
    return r


r = init_redis()

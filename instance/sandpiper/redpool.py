
import redis
from sandpiper.conf import settings

POOL = redis.ConnectionPool(
    host=settings.BASE_HOSTNAME,
    port=6379, db=0)

redpool = redis.Redis(connection_pool=POOL)
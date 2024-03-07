import redis
import os

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
r.set('foo', 'bar')
print(r.get('foo'))

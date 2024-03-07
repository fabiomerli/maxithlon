import redis

r = redis.Redis(host=${process.env.REDIS_HOST}, port=${process.env.REDIS_PORT}, db=0)
r.set('foo', 'bar')
print(r.get('foo'))

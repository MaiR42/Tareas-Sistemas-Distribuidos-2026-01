import redis

r = redis.Redis(
   host="cache",
   port=6379,
   decode_responses=True
)

print(r.ping())

r.set("prueba","hola",ex=60)

print(r.get("prueba"))

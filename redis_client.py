import redis

redis_client = redis.Redis(
    host= "localhost",  #Docker container
    port= 6379,
    decode_responses= True  # Veri str tipinde False olsaydı bytes olacaktı
)


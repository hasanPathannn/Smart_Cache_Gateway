from redis import Redis
import time

class RateLimiter:
    def __init__(self, redis_client: Redis, rate: int, capacity: int):
        self.redis = redis_client
        self.rate = rate          # Tokens added per second
        self.capacity = capacity  # Max tokens in the bucket
        
        # LUA SCRIPT: This runs atomically inside Redis
        # Keys: [1] user_key
        # Args: [1] fill_rate, [2] capacity, [3] current_timestamp, [4] tokens_requested
        self.lua_script = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])

        -- Get current bucket state
        local info = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(info[1])
        local last_refill = tonumber(info[2])

        -- Initialize if missing
        if not tokens or not last_refill then
            tokens = capacity
            last_refill = now
        end

        -- Refill tokens based on time passed
        local delta = math.max(0, now - last_refill)
        local filled_tokens = math.min(capacity, tokens + (delta * rate))

        -- Check if we have enough tokens
        local allowed = 0
        if filled_tokens >= requested then
            filled_tokens = filled_tokens - requested
            allowed = 1
        end

        -- Save new state
        redis.call('HMSET', key, 'tokens', filled_tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 60) -- Key expires if inactive for 60s

        return {allowed, filled_tokens}
        """
        self.script_sha = self.redis.script_load(self.lua_script)

    def allow_request(self, user_id: str, cost: int = 1) -> bool:
        """
        Returns True if request is allowed, False if rate limited.
        """
        key = f"rate_limit:{user_id}"
        current_time = int(time.time())
        
        try:
            # EvalSHA is faster than Eval because it uses the cached script hash
            result = self.redis.evalsha(
                self.script_sha, 
                1,              # Number of keys
                key,            # Key name
                self.rate,      # ARGV[1]
                self.capacity,  # ARGV[2]
                current_time,   # ARGV[3]
                cost            # ARGV[4]
            )
            return bool(result[0])
        except Exception as e:
            print(f"Rate Limit Error: {e}")
            # Fail open strategy: If Redis fails, allow traffic so we don't block users
            return True
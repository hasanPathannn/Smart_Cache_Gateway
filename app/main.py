from fastapi import FastAPI, BackgroundTasks, Response
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
from redis import Redis

# Importing from our new modular structure
from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.services.cache_service import SemanticCache
from app.services.rate_limiter import RateLimiter
from app.services.llm_service import LLMService

from app.services.intent_classifier import IntentClassifier

app = FastAPI(title="SmartCache Gateway")

# --- Initialize Services ---
redis_client = Redis.from_url(settings.REDIS_URL)
cache_engine = SemanticCache(redis_client)
rate_limiter = RateLimiter(redis_client, rate=settings.RATE_LIMIT_PER_SEC, capacity=settings.RATE_LIMIT_BURST)
llm_service = LLMService()
intent_classifier = IntentClassifier()

# --- Metrics ---
CACHE_HITS = Counter("smartcache_hits_total", "Number of cache hits")
CACHE_MISSES = Counter("smartcache_misses_total", "Number of cache misses")
SAVED_COST = Counter("smartcache_money_saved_usd", "Estimated money saved")

Instrumentator().instrument(app).expose(app)

# --- Background Task Helper ---
def background_cache_update(prompt: str, response: str):
    try:
        cache_engine.store_response(prompt, response)
    except Exception as e:
        print(f"Background Cache Error: {e}")

# --- API Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, response: Response, background_tasks: BackgroundTasks):
    
    # 1. Rate Limiting
    if not rate_limiter.allow_request(request.user_id):
        response.status_code = 429
        return ChatResponse(
            response="Too Many Requests. Please slow down.",
            source="rate_limiter",
            cost_incurred=False
        )

   
    # 2. NEW LOGIC: Intent Classification (The Security Guard)
    is_static = intent_classifier.is_cacheable(request.prompt)
    cached_text = None

    if is_static:
        # Only check cache if the question is "safe" (generic)
        cached_text = cache_engine.check_cache(request.prompt)
    else:
        print(f"Dynamic Intent Detected: '{request.prompt}'. Bypassing Cache.")

    # 3. Cache Hit (Only if Static AND Found)
    if cached_text:
        CACHE_HITS.inc()
        SAVED_COST.inc(0.002)
        return ChatResponse(
            response=cached_text,
            source="cache",
            latency_saved="High"
        )

    # 4. Cache Miss (Or Forced Bypass) - Call LLM
    CACHE_MISSES.inc()
    
    try:
        llm_text, provider = llm_service.get_response(request.prompt)
    except Exception as e:
        response.status_code = 500
        return ChatResponse(
            response=f"Internal Error: {str(e)}",
            source="internal_error",
            cost_incurred=False
        )
    
    # 5. Background Update (ONLY if it was static!)
    # We do NOT want to cache "My order status is pending" for everyone to see.
    if is_static:
        background_tasks.add_task(background_cache_update, request.prompt, llm_text)

    return ChatResponse(
        response=llm_text,
        source=provider, 
        cost_incurred=True
    )
import json
import numpy as np
from redis import Redis
from redis.commands.search.field import VectorField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

class SemanticCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        # Load a lightweight, fast model optimized for semantic search
        # We load this ONCE at startup to avoid latency per request
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = "idx:gpt_responses"
        self.vector_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.similarity_threshold = 0.9  # 0.9 = very similar, 0.5 = somewhat similar

        self._create_index()

    def _create_index(self):
        """Creates the Redis Vector Search Index if it doesn't exist."""
        try:
            self.redis.ft(self.index_name).info()
            print("Index already exists.")
        except:
            print("Creating Vector Index...")
            # Define schema: prompt (vector), response (text)
            schema = (
                VectorField("embedding",
                    "FLAT", # HNSW is better for scale, FLAT is simpler for <1M items
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.vector_dim,
                        "DISTANCE_METRIC": "COSINE"
                    }
                ),
                TagField("response_text") # Store the LLM response here
            )
            self.redis.ft(self.index_name).create_index(
                schema,
                definition=IndexDefinition(prefix=["cache:"], index_type=IndexType.HASH)
            )

    def get_embedding(self, text: str) -> np.ndarray:
        """Converts text to vector embedding."""
        return self.model.encode(text).astype(np.float32).tobytes()

    def check_cache(self, prompt: str):
        """
        Performs K-Nearest Neighbor (KNN) search on Redis.
        Returns cached response if similarity > threshold.
        """
        query_vector = self.get_embedding(prompt)

        # Redis Query: Find top 1 nearest neighbor
        q = Query(f"*=>[KNN 1 @embedding $vec AS score]") \
            .sort_by("score") \
            .return_fields("response_text", "score") \
            .dialect(2)
        
        params = {"vec": query_vector}
        results = self.redis.ft(self.index_name).search(q, query_params=params)

        if results.docs:
            doc = results.docs[0]
            # Redis returns 'distance' (1 - cosine_similarity). 
            # So smaller score = more similar.
            # Convert distance to similarity: similarity = 1 - distance
            distance = float(doc.score)
            
            # Note: Redis vector score behavior depends on metric. 
            # For COSINE, Redis returns 1 - cosine_similarity.
            # So if distance is 0.05, similarity is 0.95.
            
            if distance < (1 - self.similarity_threshold):
                print(f"CACHE HIT! Distance: {distance}")
                return doc.response_text
        
        print("CACHE MISS.")
        return None

    def store_response(self, prompt: str, response: str):
        """Stores the prompt embedding and response in Redis."""
        vector = self.get_embedding(prompt)
        # Unique key for Redis entry
        key = f"cache:{hash(prompt)}" 
        
        self.redis.hset(key, mapping={
            "embedding": vector,
            "response_text": response
        })
        # Set TTL (Time To Live) to 1 hour to prevent stale data
        self.redis.expire(key, 3600)
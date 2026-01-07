import time
import random

class LLMService:
    def __init__(self):
        pass

    def _call_openai_mock(self, prompt: str) -> str:
        """
        Simulates calling OpenAI. 
        Includes a 'Chaos Monkey' that randomly fails 30% of the time.
        """
        # Simulate network latency
        time.sleep(0.5)
        
        # 30% chance of Service Unavailable (Simulating an outage)
        if random.random() < 0.3:
            raise Exception("OpenAI API 503 Service Unavailable")
            
        return f"OpenAI GPT-4 Response: {prompt}"

    def _call_fallback_model(self, prompt: str) -> str:
        """
        Fallback to a cheaper/local model. Never fails.
        """
        return f"Fallback (Llama-3) Response: {prompt}"

    def get_response(self, prompt: str) -> tuple:
        """
        Orchestrates the Failover Logic.
        Returns: (response_text, provider_name)
        """
        try:
            # 1. Try Primary Provider
            response = self._call_openai_mock(prompt)
            return response, "openai"
        except Exception as e:
            # 2. Log the failure and route to Fallback
            print(f"⚠️ Primary LLM Failed: {e}. Routing to Fallback...")
            response = self._call_fallback_model(prompt)
            return response, "llama-3-fallback"
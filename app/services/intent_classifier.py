import re

class IntentClassifier:
    def __init__(self):
        # Words that indicate specific, personal user data (Dynamic)
        # These should NEVER be cached to avoid data leaks.
        self.dynamic_patterns = [
            r"\bmy\b",           # "my order", "my account"
            r"\bI\b",            # "I want to...", "I have..."
            r"\bme\b",           # "tell me about my..."
            r"\border\b",        # "order status"
            r"\baccount\b",      # "account balance"
            r"\bstatus\b",       # "status of..."
            r"\bpayment\b",      # "payment history"
            r"\bcredit card\b",
            r"\baddress\b",
            r"\bbalance\b"
        ]
        self.regex = re.compile("|".join(self.dynamic_patterns), re.IGNORECASE)

    def is_cacheable(self, prompt: str) -> bool:
        """
        Returns True if the prompt is generic/static knowledge.
        Returns False if the prompt contains personal/dynamic context.
        """
        # If we find a "personal" word, it is NOT cacheable.
        if self.regex.search(prompt):
            return False
        
        return True
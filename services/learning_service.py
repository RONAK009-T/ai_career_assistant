from services.gemini_service import call_gemini, call_gemini_json

def ask_learning_tutor(topic: str, question: str, difficulty: str = "Intermediate") -> str:
    prompt = f"Topic: {topic}\nDifficulty: {difficulty}\nQuestion: {question}"
    res = call_gemini(prompt)
    if res == "[FALLBACK_MODE]" or not res:
        return f"""### 💡 AI Tutor Explanation: {topic} ({difficulty} Level)

#### 1. Core Concept
In **{topic}**, the core principle behind *"{question}"* revolves around optimizing execution flow, data encapsulation, and predictable state management.

Think of it like an **orchestrated assembly line**: instead of running ad-hoc queries repeatedly, you structure operations into deterministic pipelines.

#### 2. Production Code Example (Python)
```python
# Production example demonstrating {topic} best practices
import time
from typing import List, Dict, Any

class OptimizedManager:
    def __init__(self, name: str):
        self.name = name
        self._cache = dict()

    def fetch_data(self, key: str) -> Any:
        # Fetches cached data or executes heavy query if missing
        if key in self._cache:
            return self._cache[key]
        
        # Simulating optimized computation / database fetch
        result = f"Computed payload for {key} in {self.name}"
        self._cache[key] = result
        return result

# Usage
manager = OptimizedManager("{topic}")
print(manager.fetch_data("primary_query"))
```

#### 3. Common Pitfalls & Edge Cases
* ⚠️ **N+1 Query Problem:** Failing to pre-fetch related entities causing quadratic database queries.
* ⚠️ **State Mutation:** Modifying default mutable arguments across multiple invocations.
* ⚠️ **Exception Handling:** Not wrapping network or I/O calls in graceful try/except contexts.

#### 4. Key Takeaway
Mastering this pattern ensures high scalability, lower latency, and clean testability in production code.
"""
    return res

def generate_quiz_questions(topic: str, difficulty: str = "Intermediate", count: int = 3) -> dict:
    prompt = f"Generate {count} MCQs on '{topic}' at '{difficulty}' difficulty."
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("questions"):
        return {
            "topic": topic,
            "difficulty": difficulty,
            "questions": [
                {
                    "id": 1,
                    "question": f"In {topic}, what is the primary advantage of using connection pooling in database-backed applications?",
                    "options": [
                        "It eliminates the need for SQL queries entirely",
                        "It reuses established database connections, reducing connection overhead and latency",
                        "It automatically converts relational data into NoSQL documents",
                        "It restricts the database to single-threaded operations"
                    ],
                    "correct_option_index": 1,
                    "explanation": "Connection pooling avoids the expensive TCP handshake and authentication overhead by maintaining a pool of warm connections."
                },
                {
                    "id": 2,
                    "question": f"Which of the following is considered an anti-pattern when writing asynchronous code in {topic}?",
                    "options": [
                        "Using non-blocking async/await calls",
                        "Executing blocking CPU-intensive synchronous operations directly on the event loop",
                        "Leveraging asyncio.gather for parallel I/O requests",
                        "Setting timeouts on external HTTP requests"
                    ],
                    "correct_option_index": 1,
                    "explanation": "Blocking operations freeze the entire event loop, preventing other concurrent tasks from progressing."
                },
                {
                    "id": 3,
                    "question": f"When designing RESTful APIs in {topic}, which HTTP status code should be returned upon successfully creating a resource?",
                    "options": [
                        "200 OK",
                        "201 Created",
                        "204 No Content",
                        "301 Moved Permanently"
                    ],
                    "correct_option_index": 1,
                    "explanation": "HTTP 201 Created explicitly indicates that the request has succeeded and led to the creation of a new resource."
                }
            ]
        }
    return res

def generate_coding_exercise(topic: str, difficulty: str = "Intermediate") -> dict:
    prompt = f"Generate coding challenge for {topic} at {difficulty} level."
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("title"):
        return {
            "title": f"LRU Cache Optimization in {topic}",
            "difficulty": difficulty,
            "problem_statement": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache with O(1) time complexity for both get() and put() operations.",
            "examples": [
                {"input": "lru = LRUCache(2); lru.put(1, 1); lru.put(2, 2); lru.get(1)", "output": "1"},
                {"input": "lru.put(3, 3); lru.get(2)", "output": "-1 (evicted)"}
            ],
            "hints": ["Use a combination of a HashMap and a Doubly Linked List", "Collections.OrderedDict in Python provides built-in O(1) reordering"],
            "starter_code": "class LRUCache:\n    def __init__(self, capacity: int):\n        self.capacity = capacity\n\n    def get(self, key: int) -> int:\n        # Implement get\n        return -1\n\n    def put(self, key: int, value: int) -> None:\n        # Implement put\n        pass",
            "solution_code": "from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity: int):\n        self.cap = capacity\n        self.cache = OrderedDict()\n\n    def get(self, key: int) -> int:\n        if key not in self.cache:\n            return -1\n        self.cache.move_to_end(key)\n        return self.cache[key]\n\n    def put(self, key: int, value: int) -> None:\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.cap:\n            self.cache.popitem(last=False)",
            "explanation": "OrderedDict preserves insertion order while move_to_end() executes in O(1) time, ensuring constant time eviction of the oldest item."
        }
    return res

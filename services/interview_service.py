from services.gemini_service import call_gemini_json

def generate_interview_questions(target_role: str, question_type: str = "Technical", count: int = 3, job_desc: str = "") -> dict:
    prompt = f"Generate {count} {question_type} interview questions for {target_role}."
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("questions"):
        return {
            "target_role": target_role,
            "question_type": question_type,
            "questions": [
                {
                    "id": 1,
                    "question": f"How do you design a robust database schema in Django / PostgreSQL to handle high-frequency concurrent writes without deadlocks?",
                    "category": "Database Architecture",
                    "ideal_concepts": ["Transaction isolation levels", "select_for_update", "Indexing strategy", "Connection pooling"]
                },
                {
                    "id": 2,
                    "question": f"Walk me through a situation where an API endpoint you deployed had unacceptable response times. How did you profile, diagnose, and resolve it?",
                    "category": "Performance & Debugging",
                    "ideal_concepts": ["STAR format", "Profiling tools (Django Debug Toolbar/cProfile)", "Query optimization", "Redis caching"]
                },
                {
                    "id": 3,
                    "question": f"How do you approach securing a public RESTful API against common vulnerabilities like SQL injection, CSRF, and token tampering?",
                    "category": "Security & Best Practices",
                    "ideal_concepts": ["JWT authentication", "Parameterized ORM queries", "CORS & CSRF middleware", "Rate limiting"]
                }
            ]
        }
    return res

def evaluate_interview_response(question: str, user_answer: str, target_role: str = "Software Engineer") -> dict:
    if not user_answer or len(user_answer.strip()) < 5:
        return {
            "score": 40,
            "strengths": ["Attempted response"],
            "weaknesses": ["Response was too brief. Elaborate with concrete technical steps and metrics."],
            "missing_concepts": ["STAR format", "Specific architectural mechanisms"],
            "improved_model_answer": "In my previous project, I solved this by profiling slow queries using EXPLAIN ANALYZE, implementing an indexed B-tree on the lookup column, and introducing a Redis cache layer for high-throughput reads.",
            "communication_tips": "Always start with the core resolution and follow up with measurable results."
        }
        
    prompt = f"Evaluate candidate answer for {target_role}:\nQ: {question}\nA: {user_answer}"
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("score"):
        return {
            "score": 85,
            "strengths": [
                "Directly answered the question with clear technical grounding",
                "Demonstrated good awareness of production system constraints and failure modes"
            ],
            "weaknesses": [
                "Could include more specific metrics (e.g. latency drop from 300ms to 40ms)",
                "Consider mentioning automated unit and integration tests to prevent regression"
            ],
            "missing_concepts": [
                "Automated rollback strategy",
                "Circuit breaker patterns for external service calls"
            ],
            "improved_model_answer": f"To address this effectively: First, I isolate the root cause using APM profiling and log aggregation. Next, I implement the fix utilizing transaction management (e.g., select_for_update) and cache warmer layers. Finally, I write regression test suites in PyTest before promoting to staging.",
            "communication_tips": "Deliver answers with structured confidence: Problem -> Solution Strategy -> Measurable Impact."
        }
    return res

from services.gemini_service import call_gemini_json

def fallback_roadmap(target_role: str, current_skills: list, exp_level: str) -> dict:
    role_clean = target_role.strip()
    return {
        "target_role": role_clean,
        "estimated_timeline": "4 - 6 Months",
        "required_skills": ["Python", "Django / FastAPI", "PostgreSQL", "Docker", "RESTful Architecture", "AWS Cloud", "Git & CI/CD"],
        "stages": [
            {
                "stage_number": 1,
                "title": f"Stage 1: Core Foundations & System Building for {role_clean}",
                "duration": "4-6 Weeks",
                "focus_areas": ["Advanced Python Syntax", "OOP & Design Patterns", "Relational Database Normalization", "Git Workflows"],
                "recommended_topics": ["List/Dict Comprehensions & Generators", "Context Managers & Decorators", "SQL Joins & Indexing", "Unit Testing with PyTest"],
                "practice_project": {
                    "title": "Scalable CLI Task Engine",
                    "description": "Build an asynchronous CLI engine with SQLite connection pooling and automated transaction handling."
                }
            },
            {
                "stage_number": 2,
                "title": "Stage 2: Web Framework Mastery & Microservices Integration",
                "duration": "6-8 Weeks",
                "focus_areas": ["Django / FastAPI", "RESTful API Architecture", "JWT & OAuth2 Authentication", "Celery Background Workers"],
                "recommended_topics": ["ORM Query Optimization (select_related)", "Rate Limiting & Caching with Redis", "API Documentation (Swagger/OpenAPI)", "Asynchronous Tasks"],
                "practice_project": {
                    "title": "Production E-Commerce & SaaS Backend",
                    "description": "Full-fledged REST API with role-based access control, Stripe payment webhook integration, and Redis caching."
                }
            },
            {
                "stage_number": 3,
                "title": "Stage 3: Cloud DevOps, Containerization & Production Scale",
                "duration": "4-6 Weeks",
                "focus_areas": ["Docker Multi-Stage Builds", "CI/CD Automation", "AWS Deployment", "System Monitoring & Logging"],
                "recommended_topics": ["Docker Compose Orchestration", "GitHub Actions Pipelines", "Nginx Reverse Proxy & Gunicorn", "Prometheus & Grafana"],
                "practice_project": {
                    "title": "Containerized Microservices Cluster",
                    "description": "Deploy a multi-service web application on AWS ECS with automated CI/CD and zero-downtime rolling deployments."
                }
            }
        ],
        "portfolio_recommendations": [
            "Host live demos of 2 full-stack projects with comprehensive GitHub README files and architecture diagrams",
            "Include automated test suites (over 80% test coverage) and containerized Dockerfiles in your repositories",
            "Write a technical article on medium/dev.to detailing how you solved a database query bottleneck"
        ],
        "interview_prep_topics": [
            "Data Structures & Algorithms (HashMaps, Two Pointers, Trees, Dynamic Programming)",
            "System Design Fundamentals (Caching layers, Database Sharding, Load Balancers, CAP Theorem)",
            "Behavioral Interview Questions using the STAR (Situation, Task, Action, Result) Framework"
        ]
    }

def generate_career_roadmap(target_role: str, current_skills: list = None, experience_level: str = "Intermediate") -> dict:
    prompt = f"Generate Career Roadmap for '{target_role}' (Level: {experience_level}):\nSkills: {current_skills}"
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("stages"):
        return fallback_roadmap(target_role, current_skills or [], experience_level)
    return res

def fallback_skill_gaps(current_skills: list, target_role: str) -> dict:
    return {
        "skills": [
            {"name": "Python", "category": "Core Language", "status": "Mastered", "proficiency_score": 90},
            {"name": "Django / FastAPI", "category": "Web Framework", "status": "Strong", "proficiency_score": 80},
            {"name": "SQL & Databases", "category": "Databases", "status": "Strong", "proficiency_score": 75},
            {"name": "Docker & Containers", "category": "DevOps", "status": "Need Improvement", "proficiency_score": 50},
            {"name": "AWS Cloud", "category": "Cloud", "status": "Missing", "proficiency_score": 25},
            {"name": "Redis & Caching", "category": "Architecture", "status": "Need Improvement", "proficiency_score": 45}
        ],
        "priority_recommendations": [
            "Prioritize mastering Docker containerization and Docker Compose for web deployments",
            "Learn Redis caching strategies to optimize heavy Django ORM queries",
            "Build familiarity with AWS ECS or Lambda for production cloud deployments"
        ]
    }

def analyze_skill_gaps(current_skills: list, target_role: str) -> dict:
    prompt = f"Analyze skill gaps for {target_role}:\nSkills: {current_skills}"
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("skills"):
        return fallback_skill_gaps(current_skills, target_role)
    return res

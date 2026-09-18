from services.gemini_service import call_gemini

def generate_professional_email(email_type: str, recipient: str, company: str, context: str, key_points: str, tone: str = "Professional") -> str:
    prompt = f"Write {email_type} email to {recipient} at {company}. Tone: {tone}. Context: {context}. Highlights: {key_points}"
    res = call_gemini(prompt)
    if res == "[FALLBACK_MODE]" or not res:
        recip_name = recipient or "Hiring Team"
        comp_name = company or "Target Company"
        
        return f"""Subject: Application / Inquiry: Senior Full Stack Developer — {comp_name}

Dear {recip_name},

I hope this email finds you well.

I am writing to express my strong interest in joining {comp_name}. Having closely followed your team's engineering innovations and recent milestones, I am eager to contribute my full-stack and backend development background to your mission.

Key Highlights of My Experience:
• Demonstrable background in Python, scalable web frameworks (Django/FastAPI), and relational database optimization.
• Proven track record of architecting resilient REST APIs, microservices, and automated testing pipelines.
• {key_points or 'Passionate about building performant, secure, and user-centric software products.'}

Context & Portfolio:
{context or 'I have attached my updated resume and live portfolio links for your review. I would welcome the opportunity to discuss how my technical skills align with your current engineering goals.'}

Thank you for your time and consideration. I look forward to the possibility of speaking with you.

Best regards,

[Your Name]
[Your Phone Number] | [Your LinkedIn Profile] | [Your GitHub Portfolio]
"""
    return res

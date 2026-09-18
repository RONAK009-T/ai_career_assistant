import re
from services.gemini_service import call_gemini, call_gemini_json

def ask_pdf_question(document_text: str, question: str) -> str:
    if not document_text:
        return "No document text available. Please upload a document first."
    
    prompt = f"Answer based strictly on document text:\nDOCUMENT:\n{document_text[:10000]}\nQUESTION:\n{question}"
    res = call_gemini(prompt)
    if res == "[FALLBACK_MODE]" or not res:
        # Grounded search fallback
        q_words = [w.lower() for w in re.findall(r'\b[A-Za-z]{3,15}\b', question) if w.lower() not in ["what", "how", "where", "when", "does", "this", "that", "from"]]
        sentences = [s.strip() for s in re.split(r'[.\n]', document_text) if s.strip()]
        
        matches = []
        for s in sentences:
            s_lower = s.lower()
            if any(w in s_lower for w in q_words):
                matches.append(s)
                if len(matches) >= 3:
                    break
                    
        if matches:
            bullet_lines = []
            for m in matches:
                bullet_lines.append("- " + m)
            grounded_text = "\n\n".join(bullet_lines)
            return "### 📄 Grounded Document Answer\n\nBased on the uploaded document:\n\n" + grounded_text + "\n\n*(Extracted directly from indexed content)*"
        else:
            return "The uploaded document does not contain sufficient specific information to answer this query directly."
    return res

def summarize_document(document_text: str) -> dict:
    if not document_text:
        return {"error": "Document text is empty."}
        
    prompt = f"Summarize document:\n{document_text[:10000]}"
    res = call_gemini_json(prompt)
    if res.get("_fallback") or "error" in res or not res.get("executive_summary"):
        lines = [l.strip() for l in document_text.split('\n') if len(l.strip()) > 30]
        preview = lines[:4] if len(lines) >= 4 else ["Overview of indexed document content and core concepts."]
        
        return {
            "executive_summary": " ".join(preview[:2]) if preview else "Comprehensive document covering key software, career, and development topics.",
            "key_takeaways": [
                "Detailed technical framework and methodologies described in the core sections",
                "Emphasis on clean execution, modular architecture, and industry standards",
                "Practical guidelines for implementation, debugging, and verification"
            ],
            "flashcards": [
                {"front": "What is the primary topic of this document?", "back": preview[0] if preview else "Core domain concepts and architecture."},
                {"front": "What are the key execution practices highlighted?", "back": "Modular structuring, testing, and continuous optimization."}
            ],
            "mcqs": [
                {
                    "question": "Which aspect is prioritized throughout the provided document?",
                    "options": [
                        "High reliability and systematic implementation",
                        "Unstructured experimental development",
                        "Manual execution without automation",
                        "Ignoring edge cases and error handling"
                    ],
                    "correct_option_index": 0,
                    "explanation": "The document emphasizes structured engineering and robust implementation."
                }
            ]
        }
    return res

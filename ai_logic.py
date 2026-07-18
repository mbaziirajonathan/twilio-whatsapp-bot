import os
import io
import json
import re
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Init Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def get_client():
    return client

# Load NCDC syllabus - structure: { "S1": {"Physics": [...], "Chemistry": [...], "Biology": [...]},... }
try:
    with open("syllabus.json", "r", encoding="utf-8") as f:
        SYLLABUS = json.load(f)
except:
    SYLLABUS = {}

def get_topic_context(user_msg):
    """Detect level, subject, topic from NCDC syllabus"""
    user_msg = user_msg.lower()
    for level, subjects in SYLLABUS.items():
        for subject, topics in subjects.items():
            for topic in topics:
                if topic.lower() in user_msg:
                    return f"Level: {level}, Subject: {subject}, Topic: {topic}"
    return "General S1-S6 Science Question"

def generate_ai_response(user_msg, chat_history=[]):
    """Main brain function called by main.py"""
    try:
        topic_context = get_topic_context(user_msg)
        
        system_prompt = f"""
You are "NCDC UNEB Science Tutor Bot" for Uganda Secondary Schools S1 to S6.
You strictly follow the NCDC syllabus and UNEB exam style for Physics, Chemistry, and Biology.

Current context: {topic_context}

TEACHING RULES:
1. **NCDC Alignment**: Teach by competencies. Start with "Learning Outcome", then explanation, then example.
2. **UNEB Exam Style**: 
   - Definitions: 1-2 lines, key terms
   - Explanations: 4-5 points with examples from Uganda context
   - Calculations: Formula, Substitution, Working, Final Answer + Units
   - Diagrams: Describe clearly. "Draw and label:..."
   - Practicals: State apparatus, procedure, observation, conclusion
3. **Subject Specific**:
   **Physics**: Emphasize formulas, SI units, experiments, real-life applications.
   **Chemistry**: Balance equations, state symbols, mole calculations, lab safety, periodic trends.
   **Biology**: Processes, functions, adaptations, Ugandan examples, diseases, environment.
4. **Levels**: Adjust depth. S1-S2 = simple. S3-S4 O'Level = past paper style. S5-S6 A'Level = detailed, derivations.
5. **WhatsApp Format**: Short, clear, use **Bold labels**. Max 4-5 paragraphs. Use bullets.
6. **Language**: Simple English. If student asks "in Luganda", translate key terms.
7. **Out of Scope**: "I only teach Physics, Chemistry and Biology S1-S6 as per NCDC. Ask me about those!"

Always be encouraging and help students pass UNEB.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history for memory
        for role, content in chat_history[-6:]: # last 3 exchanges
            messages.append({"role": role, "content": content})
            
        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.5, # Lower for more factual NCDC answers
            max_tokens=600
        )
        
        reply = response.choices[0].message.content
        return reply.strip()
        
    except Exception as e:
        print("GROQ ERROR:", e)
        return "Sorry, my brain is thinking too hard. Please ask again in 10 seconds."

def process_query(user_msg, chat_history=[]):
    """Wrapper so main.py can call this"""
    return generate_ai_response(user_msg, chat_history)

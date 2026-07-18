# ai_logic.py
import os, io, json, re, numpy as np, random
import pandas as pd
import plotly.express as px
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from pathlib import Path
from gtts import gTTS

# PASTE YOUR FULL SYLLABUS + PRACTICALS HERE FROM app.py
SYLLABUS = {...}
PRACTICALS = {...}

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

def get_client():
    api_key = os.getenv("GROQ_API_KEY") # Use.env, not st.secrets for API
    if not api_key: raise ValueError("GROQ_API_KEY not found in.env")
    return Groq(api_key=api_key)

def is_in_syllabus(query: str, subject: str, class_level: str) -> bool:
    """Check if topic is in NCDC 2026 syllabus to reduce hallucination"""
    topics = " ".join(SYLLABUS.get(subject, {}).get(class_level, [])).lower()
    return any(word in topics for word in query.lower().split() if len(word) > 3)

def generate_ai_response(client, prompt, subject, class_level):
    # ANTI-HALLUCINATION SYSTEM PROMPT
    system_prompt = f"""You are UCE/UACE DIGITAL TUTOR 2026.
    CRITICAL RULES:
    1. You ONLY teach {subject} for {class_level} in Uganda.
    2. You MUST follow NCDC Uganda Syllabus 2026 ONLY. Topics: {SYLLABUS[subject][class_level]}
    3. If the question is NOT in the syllabus above, you MUST reply exactly: "This topic is outside NCDC 2026 syllabus for {subject} {class_level}. I cannot answer it."
    4. Use Ugandan examples. Be factual, step-by-step. Cite UNEB style.
    5. Never make up formulas, dates, or facts.
    """

    # Pre-check to save API cost
    if not is_in_syllabus(prompt, subject, class_level):
        return f"This topic is outside NCDC 2026 syllabus for {subject} {class_level}. I cannot answer it."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.1, # LOW = less creative, more factual
            max_tokens=800,
            top_p=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Could not reach AI. Please try again. Error: {str(e)}"

# PASTE ALL YOUR OTHER FUNCTIONS: generate_graph, create_pdf, find_diagram, generate_tts

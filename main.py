from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os

from database import init_db, save_message, get_chat_history, clear_history
from ai_logic import process_query

load_dotenv()

app = FastAPI(title="NCDC UNEB Science Tutor Bot")

# Run once when Render starts
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized")

@app.get("/")
def home():
    return {"status": "NCDC UNEB Science Tutor Bot is Live", "subjects": ["Physics", "Chemistry", "Biology"]}

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Twilio sends POST here"""
    form = await request.form()
    user_msg = form.get("Body", "").strip()
    phone = form.get("From", "")

    print(f"Message from {phone}: {user_msg}")

    # Handle reset command
    if user_msg.lower() in ["reset", "clear", "new chat"]:
        clear_history(phone)
        resp = MessagingResponse()
        resp.message("History cleared. Let's start fresh! Ask me any S1-S6 Physics, Chemistry, or Biology question.")
        return Response(content=str(resp), media_type="application/xml")

    # 1. Get chat history from DB for context
    history = get_chat_history(phone, limit=6) # last 3 Q&A

    # 2. Get AI response with NCDC/UNEB prompt
    try:
        ai_reply = process_query(user_msg, history)
    except Exception as e:
        print("AI ERROR:", e)
        ai_reply = "Sorry, I had a problem thinking. Please try again."

    # 3. Save to DB
    save_message(phone, "user", user_msg)
    save_message(phone, "assistant", ai_reply)

    # 4. Reply back to Twilio
    resp = MessagingResponse()
    resp.message(ai_reply)

    return Response(content=str(resp), media_type="application/xml")

@app.get("/webhook")
def verify_webhook():
    """For Render health check"""
    return {"status": "webhook is running"}

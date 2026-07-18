# main.py
from fastapi import FastAPI, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from twilio.rest import Client
from ai_logic import get_client, generate_ai_response
from database import get_session, save_session, log_activity
import os, traceback, time
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="UCE Tutor WhatsApp API v1.0")
client = get_client()

ADMIN_NUMBER = "256751040731"
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = 'whatsapp:+14155238886' # Sandbox number
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID else None

LAST_REQUEST = {}
def is_rate_limited(phone: str, seconds=3):
    now = time.time()
    if phone in LAST_REQUEST and now - LAST_REQUEST[phone] < seconds: return True
    LAST_REQUEST[phone] = now
    return False

def parse_command(message: str):
    msg_lower = message.lower()
    subject, class_level = "Biology", "S4"
    if "physics" in msg_lower: subject = "Physics"
    elif "chemistry" in msg_lower: subject = "Chemistry"
    for i in ["S1","S2","S3","S4"]:
        if i.lower() in msg_lower: class_level = i; break
    return subject, class_level, message

@app.post("/webhook", response_class=PlainTextResponse)
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        form = await request.form()
        from_number = form.get("From", "").replace("whatsapp:", "").replace("+", "")
        message = form.get("Body", "").strip()
        if not from_number or not message: return "Send a message to start"

        if is_rate_limited(from_number): return "⚡ Please wait 3 seconds"

        subject, class_level, clean_message = parse_command(message)
        background_tasks.add_task(process_message, from_number, clean_message, subject, class_level)
        return "🤖 UCE Tutor is typing..." # Instant reply to avoid Twilio timeout

    except Exception as e:
        print(f"[WEBHOOK CRASH] {traceback.format_exc()}")
        return "System error. Admin notified."

def process_message(from_number, message, subject, class_level):
    try:
        chat_history, activities_log = get_session(from_number, subject, class_level)
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-6:]])
        full_prompt = f"History:\n{history_text}\n\nNew Question: {message}"

        ai_reply = generate_ai_response(client, full_prompt, subject, class_level) # Anti-hallucination here

        chat_history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": ai_reply}])
        save_session(from_number, subject, class_level, chat_history, activities_log)
        log_activity(from_number, subject, class_level, f"WhatsApp: {message}")

        # SEND BACK TO WHATSAPP
        if twilio_client:
            twilio_client.messages.create(from_=TWILIO_FROM, body=ai_reply, to=f'whatsapp:+{from_number}')
        print(f"[SENT TO {from_number}]: {ai_reply[:50]}...")

    except Exception as e:
        print(f"[PROCESS CRASH] {traceback.format_exc()}")
        if twilio_client:
            twilio_client.messages.create(from_=TWILIO_FROM, body="Sorry, system error. Try again.", to=f'whatsapp:+{from_number}')

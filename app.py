from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import traceback

# Import your dissected brain
import main
import logic

load_dotenv()  # loads GROQ_API_KEY from .env or Render Env Vars

app = Flask(__name__)

# This is what Twilio will hit
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    try:
        # 1. Get message from WhatsApp user
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        print(f"Message from {from_number}: {incoming_msg}")

        if not incoming_msg:
            reply = "Send me a physics question and I’ll help you solve it 💡"
        else:
            # 2. Call your dissected brain from main.py/logic.py
            # Adjust this function name to match what you had in streamlit
            # Common ones: get_response, run_bot, process_message
            reply = main.get_bot_response(incoming_msg) 
            
            # If your streamlit used logic.py directly, do:
            # reply = logic.process_query(incoming_msg)

        # 3. Send reply back to Twilio
        resp = MessagingResponse()
        resp.message(reply)
        return str(resp)

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        resp = MessagingResponse()
        resp.message("Oops, my brain crashed. Try asking again in 10 seconds.")
        return str(resp)


@app.route("/", methods=['GET'])
def health_check():
    return "Twilio Physics Bot is running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

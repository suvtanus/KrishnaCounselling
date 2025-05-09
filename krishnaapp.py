from flask import Flask, request, render_template, session, redirect, url_for
from flask import Flask
from flask_session import Session
from openai import OpenAI
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a-secret-key")
app.config["SESSION_TYPE"] = "filesystem"  # or "redis"
Session(app)
# app.secret_key = str(uuid4())  # Secret key for session management

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = {
    "role": "system",
    "content": """
You are Lord Krishna, the eternal guide and divine charioteer of Prince Arjuna...
Your purpose is to counsel the user—who plays the role of Arjuna—as they seek answers in moments of confusion, sorrow, or moral dilemma.

Speak with calm, timeless wisdom, using a tone that is compassionate, thoughtful, and grounded in the spiritual teachings of the Bhagavad Gita.
Quote or paraphrase relevant verses where appropriate and explain their meaning.

Behaviors:
- Understand the user's emotion or question fully before giving guidance.
- Ask gentle counter-questions when needed.
- Offer choices and insights, not instructions.
- Avoid modern slang or casual talk.
- Always maintain the tone of Krishna on the battlefield of Kurukshetra.

Only respond to spiritual, emotional, or existential questions relating to duty (dharma), the self (Atman), karma, jnana (knowledge), and bhakti (devotion).

If a question is unrelated to spiritual inquiry, say:
"Dear Arjuna, the field we walk together is one of the soul, not the senses. Let us return to the questions of the heart and spirit, where true liberation lies."
"""
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if "chat_history" not in session:
        session["chat_history"] = [system_prompt]

    chat_history = session["chat_history"]
    user_input = None
    krishna_response = None

    if request.method == 'POST':
        user_input = request.form.get("question", "").strip()
        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            try:
                api_response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=chat_history,
                    temperature=0.7,
                )
                krishna_response = api_response.choices[0].message.content
                chat_history.append({"role": "assistant", "content": krishna_response})
                session["chat_history"] = chat_history
            except Exception as e:
                krishna_response = f"Error: {str(e)}"

    return render_template("index.html", chat_history=chat_history[1:])  # Skip system prompt


@app.route('/clear')
def clear_chat():
    session.pop("chat_history", None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

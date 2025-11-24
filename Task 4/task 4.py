python3 -m venv .venv

.venv\Scripts\activate         # Windows
import os
import streamlit as st
from google import genai
from google.genai import types

# --------------------------------------------------
# 1. Gemini Initialization
# --------------------------------------------------

os.environ["GEMINI_API_KEY"] = "XXXXXXXXX"

client = genai.Client()

def ask_gemini(question: str) -> str:
    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a friendly medical assistant. "
            "Explain general health topics in simple terms. "
            "Do NOT tell anyone to take medication or diagnose conditions. "
            "Focus on causes, prevention, and general tips only."
        ),
        temperature=0.7
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=config
    )

    return response.text

def safety_check(answer: str) -> str:
    forbidden_phrases = ["take medication", "prescribe", "perform surgery", "diagnose"]
    for phrase in forbidden_phrases:
        if phrase in answer.lower():
            answer = answer.lower().replace(phrase, "[general info only]")
    return answer


# --------------------------------------------------
# 2. Streamlit UI Styling
# --------------------------------------------------

st.set_page_config(page_title="Health Assistant", page_icon="💬")

st.markdown("""
    <style>
        .chat-container {
            max-width: 550px;
            margin: auto;
        }
        .user-bubble {
            background-color: #dcf8c6;
            padding: 12px 15px;
            border-radius: 15px;
            margin: 6px;
            max-width: 75%;
            align-self: flex-end;
            color: black;
        }
        .bot-bubble {
            background-color: #ffffff;
            padding: 12px 15px;
            border-radius: 15px;
            margin: 6px;
            max-width: 75%;
            border: 1px solid #ddd;
            color: black;
        }
        .chat-box {
            display: flex;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Health Assistant")


# --------------------------------------------------
# 3. Chat History
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 4. Display Chat
# --------------------------------------------------

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='chat-box'><div class='user-bubble'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='chat-box'><div class='bot-bubble'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# 5. Input Area
# --------------------------------------------------

user_input = st.text_input("Type your message...")

if st.button("Send"):
    if user_input.strip():

        # Save user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get bot response
        raw = ask_gemini(user_input)
        safe = safety_check(raw)

        st.session_state.messages.append({"role": "bot", "content": safe})

        # STREAMLIT FIX → use st.rerun() (experimental_api removed)
        st.rerun()


import random
from datetime import datetime
from io import BytesIO
import base64
import streamlit as st

# Safe import for gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed, audio will not work.")

# Optional: geolocation for country
try:
    import geocoder
except ModuleNotFoundError:
    geocoder = None

HELP_TEXT = (
    "You can ask me about the time, date, calculations, jokes, or smart questions.\n"
    "Smart questions you can ask:\n"
    "- 'What is my country?'\n"
    "- 'Current world situation?'\n"
    "General: hello, how are you, help.\n"
    "Type 'exit' to quit."
)

# ---------- AUTOPLAY AUDIO ----------
def autoplay_audio(audio_bytes: bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    unique_id = random.randint(100000, 999999)
    html = f"""
        <audio id="azile_audio_{unique_id}" autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("azile_audio_{unique_id}");
            if (audio) {{
                audio.play().catch(function(e) {{
                    console.log("Autoplay blocked:", e);
                }});
            }}
        </script>
    """
    st.components.v1.html(html, height=0)

# ---------- SPEAK ----------
def speak(text: str):
    st.session_state.chat.append(("Assistant", text))
    if GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang="en")
            audio_buf = BytesIO()
            tts.write_to_fp(audio_buf)
            st.session_state.last_audio = audio_buf.getvalue()
        except Exception as e:
            print("gTTS error:", e)
            st.session_state.last_audio = None
    else:
        st.session_state.last_audio = None

# ---------- FEATURES ----------
def tell_time(): speak(f"The current time is {datetime.now():%H:%M:%S}.")
def tell_date(): speak(f"Today is {datetime.now():%A, %B %d, %Y}.")
def tell_joke():
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why don't scientists trust atoms? Because they make up everything.",
        "I would tell you a construction pun, but I'm still working on it.",
    ]
    speak(random.choice(jokes))

def calculate(user_input: str):
    expr = user_input.partition("calculate")[2].strip()
    try:
        result = eval(expr, {"__builtins__": None}, {})
        speak(f"The result is {result}.")
    except Exception:
        speak("Sorry, I couldn't calculate that.")

def my_country():
    if geocoder:
        g = geocoder.ip('me')
        if g.ok:
            speak(f"You are currently in {g.country}.")
            return
    speak("Sorry, I could not detect your country.")

def world_situation():
    speak("The current world situation is dynamic with ongoing events and news. Stay updated with reliable sources.")

# ---------- QUERY HANDLER ----------
def handle_query(user_input: str) -> bool:
    text = user_input.lower()
    if text == "exit":
        speak("Goodbye! Have a great day!")
        return False
    elif "hello" in text or "hi" in text:
        speak("Hello! How can I assist you today?")
    elif "how are you" in text:
        speak("I am doing well, thank you! How can I assist you today?")
    elif "what is your name" in text or "your name" in text:
        speak("My name is Azile, your virtual assistant.")
    elif "who created you" in text or "creator" in text:
        speak("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in text or "capabilities" in text:
        speak("I can answer simple questions, tell time and date, jokes, calculations, and smart questions.")
    elif "help" in text or "assist" in text:
        speak(HELP_TEXT)
    elif "time" in text:
        tell_time()
    elif "date" in text:
        tell_date()
    elif "joke" in text:
        tell_joke()
    elif text.startswith("calculate"):
        calculate(user_input)
    elif "country" in text:
        my_country()
    elif "world situation" in text or "current situation" in text:
        world_situation()
    else:
        speak("Sorry, I don't understand that yet. " + HELP_TEXT)
    return True

# ---------- MAIN APP ----------
def main():
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None

    # Theme
    theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

    if theme == "Dark":
        bg = "#111111"
        fg = "#f0f0f0"
        sidebar_bg = "#1a1a1a"
        chat_bg = "#1e1e1e"
        chat_border = "#333333"
        input_bg = "#2a2a2a"
        input_border = "#444444"
        btn_bg = "#2a2a2a"
        btn_border = "#555555"
    else:
        bg = "#ffffff"
        fg = "#111111"
        sidebar_bg = "#f5f5f5"
        chat_bg = "#f9f9f9"
        chat_border = "#dddddd"
        input_bg = "#ffffff"
        input_border = "#cccccc"
        btn_bg = "#f0f0f0"
        btn_border = "#cccccc"

    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="block-container"], section.main {{
        background-color: {bg} !important;
        color: {fg} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {fg} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {fg} !important;
    }}
    p, span, div, label {{
        color: {fg} !important;
    }}
    .stMarkdown p, .stMarkdown li, .stMarkdown span {{
        color: {fg} !important;
    }}
    .chat-box {{
        background-color: {chat_bg} !important;
        border: 1px solid {chat_border} !important;
        border-radius: 10px;
        padding: 16px;
        height: 220px;
        overflow-y: auto;
        margin-bottom: 12px;
    }}
    .chat-box p, .chat-box strong {{
        color: {fg} !important;
    }}
    .stTextInput input {{
        background-color: {input_bg} !important;
        color: {fg} !important;
        border: 1px solid {input_border} !important;
    }}
    .stButton > button, .stFormSubmitButton > button {{
        background-color: {btn_bg} !important;
        color: {fg} !important;
        border: 1px solid {btn_border} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.title("Azile – Virtual Assistant - Developed by Saadman Sakib")
    st.markdown("### Introduction")
    st.markdown(HELP_TEXT)

    # ---------- CHAT HISTORY (above input) ----------
    chat_html = f'<div class="chat-box" id="chat-box">'
    if not st.session_state.chat:
        chat_html += f'<p style="color:#aaa; text-align:center; margin-top:80px;">Your conversation will appear here.</p>'
    else:
        for who, msg in st.session_state.chat:
            chat_html += f'<p><strong>{who}:</strong> {msg}</p>'
    chat_html += '</div>'
    chat_html += '<script>var cb=document.getElementById("chat-box");if(cb)cb.scrollTop=cb.scrollHeight;</script>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # ---------- USER INPUT FORM ----------
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:")
        send = st.form_submit_button("Send")
        if send and user_input.strip():
            st.session_state.last_audio = None
            st.session_state.chat.append(("You", user_input.strip()))
            cont = handle_query(user_input.strip())
            if not cont:
                st.session_state.chat.append(("Assistant", "Session ended."))
            st.rerun()

    # Auto-play audio
    if st.session_state.last_audio:
        autoplay_audio(st.session_state.last_audio)
        st.session_state.last_audio = None

    # Clear history
    if st.button("Clear history"):
        st.session_state.chat = []
        st.session_state.last_audio = None
        st.rerun()

if __name__ == "__main__":
    main()
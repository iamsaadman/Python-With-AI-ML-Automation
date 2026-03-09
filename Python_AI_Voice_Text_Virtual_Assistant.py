import random
from datetime import datetime
from io import BytesIO
import base64
import streamlit as st

st.set_page_config(page_title="Azile", page_icon="🤖", layout="centered")

# Safe import for gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False

try:
    import geocoder
except ModuleNotFoundError:
    geocoder = None

HELP_TEXT = (
    "You can ask me about the **time**, **date**, **calculations**, **jokes**, or smart questions.\n\n"
    "Try asking:\n"
    "- *What is my country?*\n"
    "- *Current world situation?*\n"
    "- *Tell me a joke*\n"
    "- *Calculate 25 * 4*\n"
    "- *What time is it?*"
)

# ── GPT-style CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #212121 !important;
    font-family: 'Sora', sans-serif;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebar"] { background: #171717 !important; }

/* Page layout */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Title bar */
.azile-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 56px;
    background: #212121;
    border-bottom: 1px solid #2f2f2f;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.azile-header h1 {
    font-size: 17px;
    font-weight: 600;
    color: #ececec;
    margin: 0;
    letter-spacing: 0.02em;
}

/* Scrollable chat area */
.chat-scroll {
    position: fixed;
    top: 56px;
    bottom: 88px;
    left: 0; right: 0;
    overflow-y: auto;
    padding: 32px 0 16px;
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* Message rows */
.msg-row {
    width: 100%;
    max-width: 720px;
    margin: 0 auto;
    padding: 12px 24px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}
.msg-row.user-row { justify-content: flex-end; }
.msg-row.bot-row  { justify-content: flex-start; background: #2a2a2a; border-radius: 12px; }

/* Avatars */
.avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
}
.avatar.user { background: #10a37f; color: white; font-weight: 600; }
.avatar.bot  { background: #444654; color: white; }

/* Bubbles */
.bubble {
    font-size: 15px;
    line-height: 1.65;
    color: #ececec;
    max-width: 600px;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble.user-bubble {
    background: #2f2f2f;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    color: #ececec;
}

/* Fixed bottom input bar */
.input-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: #212121;
    border-top: 1px solid #2f2f2f;
    padding: 12px 24px 16px;
    z-index: 1000;
}

/* Streamlit input overrides */
[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stTextInput > div > div > input {
    background: #2f2f2f !important;
    border: 1px solid #3f3f3f !important;
    border-radius: 12px !important;
    color: #ececec !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    caret-color: #10a37f;
}
.stTextInput > div > div > input:focus {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 2px rgba(16,163,127,0.18) !important;
}
.stTextInput label { display: none !important; }

/* Send button */
.stFormSubmitButton > button {
    background: #10a37f !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
.stFormSubmitButton > button:hover {
    background: #0d8f6f !important;
}

/* Clear button */
.stButton > button {
    background: transparent !important;
    color: #666 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 12px !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] * { color: #ccc !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #10a37f !important;
}

/* Push content below header and above input */
.main-spacer-top    { height: 72px; }
.main-spacer-bottom { height: 100px; }
</style>
""", unsafe_allow_html=True)

# ── Autoplay audio ─────────────────────────────────────────────────────────────
def autoplay_audio(audio_bytes: bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    uid = random.randint(100000, 999999)
    st.components.v1.html(f"""
        <audio id="az_{uid}" autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var a = document.getElementById("az_{uid}");
            if(a) a.play().catch(function(){{}});
        </script>
    """, height=0)

# ── Speak ──────────────────────────────────────────────────────────────────────
def speak(text: str):
    st.session_state.chat.append(("Assistant", text))
    if GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang="en")
            buf = BytesIO()
            tts.write_to_fp(buf)
            st.session_state.last_audio = buf.getvalue()
        except Exception as e:
            print("gTTS error:", e)
            st.session_state.last_audio = None

# ── Features ───────────────────────────────────────────────────────────────────
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
        speak(f"The result of {expr} is {result}.")
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

# ── Query handler ──────────────────────────────────────────────────────────────
def handle_query(user_input: str) -> bool:
    text = user_input.lower()
    if text == "exit":
        speak("Goodbye! Have a great day!"); return False
    elif "hello" in text or "hi" in text:
        speak("Hello! How can I assist you today?")
    elif "how are you" in text:
        speak("I am doing well, thank you! How can I assist you?")
    elif "what is your name" in text or "your name" in text:
        speak("My name is Azile, your virtual assistant.")
    elif "who created you" in text or "creator" in text:
        speak("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in text or "capabilities" in text:
        speak("I can answer questions, tell the time and date, crack jokes, do calculations, and more.")
    elif "help" in text or "assist" in text:
        speak("You can ask me about time, date, calculations, jokes, your country, or the world situation.")
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
        speak("Sorry, I don't understand that yet. Try asking for help to see what I can do.")
    return True

# ── Session state ──────────────────────────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Azile")
    st.markdown("**Your Virtual Assistant**")
    st.markdown("---")
    st.markdown(HELP_TEXT)
    st.markdown("---")
    theme = st.radio("Theme", ["Dark", "Light"], index=0)
    if st.button("🗑 Clear conversation"):
        st.session_state.chat = []
        st.session_state.last_audio = None
        st.rerun()

# Light theme override
if theme == "Light":
    st.markdown("""<style>
    html, body, [data-testid="stAppViewContainer"] { background: #f7f7f8 !important; }
    .azile-header { background: #f7f7f8; border-bottom-color: #e5e5e5; }
    .azile-header h1 { color: #111; }
    .msg-row.bot-row { background: #efefef; }
    .bubble { color: #111; }
    .bubble.user-bubble { background: #e8e8e8; color: #111; }
    .input-bar { background: #f7f7f8; border-top-color: #e5e5e5; }
    .stTextInput > div > div > input { background: #fff !important; border-color: #d9d9d9 !important; color: #111 !important; }
    </style>""", unsafe_allow_html=True)

# ── Fixed header ───────────────────────────────────────────────────────────────
st.markdown('<div class="azile-header"><h1>Azile — Virtual Assistant</h1></div>', unsafe_allow_html=True)

# ── Chat messages ──────────────────────────────────────────────────────────────
st.markdown('<div class="main-spacer-top"></div>', unsafe_allow_html=True)

if not st.session_state.chat:
    st.markdown("""
    <div style="text-align:center; padding: 80px 24px; color:#555;">
        <div style="font-size:40px; margin-bottom:16px;">🤖</div>
        <div style="font-size:20px; font-weight:600; color:#ececec; margin-bottom:8px;">How can I help you today?</div>
        <div style="font-size:14px; color:#777;">Ask me about time, date, jokes, calculations, and more.</div>
    </div>
    """, unsafe_allow_html=True)

for who, msg in st.session_state.chat:
    if who == "You":
        st.markdown(f"""
        <div class="msg-row user-row">
            <div class="bubble user-bubble">{msg}</div>
            <div class="avatar user">U</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row bot-row">
            <div class="avatar bot">🤖</div>
            <div class="bubble">{msg}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="main-spacer-bottom"></div>', unsafe_allow_html=True)

# Auto-play audio
if st.session_state.last_audio:
    autoplay_audio(st.session_state.last_audio)
    st.session_state.last_audio = None

# ── Fixed input bar ────────────────────────────────────────────────────────────
with st.container():
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("msg", placeholder="Message Azile...", label_visibility="collapsed")
        with col2:
            send = st.form_submit_button("Send ➤")
        if send and user_input.strip():
            st.session_state.last_audio = None
            st.session_state.chat.append(("You", user_input.strip()))
            cont = handle_query(user_input.strip())
            if not cont:
                st.session_state.chat.append(("Assistant", "Session ended. Refresh to start again."))
            st.rerun()
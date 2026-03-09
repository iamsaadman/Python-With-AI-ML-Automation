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
            st.session_state.last_audio = audio_buf.getvalue()  # store as bytes
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
        st.markdown("<style>body{background-color:#111;color:white}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>body{background-color:white;color:black}</style>", unsafe_allow_html=True)

    st.title("Azile – Virtual Assistant - Developed by Saadman Sakib")
    st.markdown("### Introduction")
    st.markdown(HELP_TEXT)

    # ---------- USER INPUT FORM ----------
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:")
        send = st.form_submit_button("Send")
        if send and user_input.strip():
            st.session_state.last_audio = None  # reset before new response
            st.session_state.chat.append(("You", user_input.strip()))
            cont = handle_query(user_input.strip())
            if not cont:
                st.session_state.chat.append(("Assistant", "Session ended."))

    # Render chat history
    for who, msg in st.session_state.chat:
        st.markdown(f"**{who}:** {msg}")

    # Auto-play audio — outside form, always re-rendered after state update
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
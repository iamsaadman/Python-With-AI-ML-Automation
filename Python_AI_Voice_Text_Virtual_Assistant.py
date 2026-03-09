import random
import base64
from datetime import datetime
from io import BytesIO
import time

import streamlit as st

# Safe import for gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed, audio will not work.")

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Azile – Virtual Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

HELP_TEXT = (
    "You can ask me about the time or the date, tell me to calculate something "
    "(for example: calculate 3+4), ask for a joke, or search/open a website by "
    "saying 'search' or 'open' followed by the query.  "
    "You can also say hello, ask for my name/creator, or just type 'exit' to quit."
)

# ---------- SPEAK WITH LIVE TEXT ----------
def speak_live(text: str) -> None:
    """Display text live and generate audio if available"""
    if "chat" not in st.session_state:
        st.session_state.chat = []

    st.session_state.chat.append(("Assistant", ""))
    message_index = len(st.session_state.chat) - 1
    placeholder = st.empty()

    current_text = ""
    for char in text:
        current_text += char
        st.session_state.chat[message_index] = ("Assistant", current_text)

        # Render all messages
        messages = ""
        for who, msg in st.session_state.chat:
            messages += f"**{who}:** {msg}  \n"
        placeholder.markdown(messages)
        time.sleep(0.02)

    # Generate audio if gTTS available
    if GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang="en")
            mp3_buf = BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)
            st.session_state.last_audio = base64.b64encode(mp3_buf.read()).decode()
        except Exception as e:
            print("gTTS audio error:", e)
            st.session_state.last_audio = None
    else:
        st.session_state.last_audio = None


# ---------- FEATURES ----------
def tell_time(user_name: str) -> None:
    speak_live(f"{user_name}, the current time is {datetime.now():%H:%M:%S}.")


def tell_date(user_name: str) -> None:
    speak_live(f"{user_name}, today is {datetime.now():%A, %B %d, %Y}.")


def tell_joke(user_name: str) -> None:
    jokes = [
        f"{user_name}, why did the scarecrow win an award? Because he was outstanding in his field.",
        f"{user_name}, why don't scientists trust atoms? Because they make up everything.",
        f"{user_name}, I would tell you a construction pun, but I'm still working on it.",
    ]
    speak_live(random.choice(jokes))


def calculate(user_input: str, user_name: str) -> None:
    expr = user_input.partition("calculate")[2].strip()
    try:
        result = eval(expr, {"__builtins__": None}, {})
        speak_live(f"{user_name}, the result is {result}.")
    except Exception:
        speak_live(f"{user_name}, sorry, I couldn't calculate that.")


def open_website(user_input: str, user_name: str) -> None:
    if "youtube" in user_input:
        url = "https://www.youtube.com"
    elif "google" in user_input:
        url = "https://www.google.com"
    else:
        query = user_input.replace("search", "").replace("open", "").strip()
        url = "https://www.google.com/search?q=" + query.replace(" ", "+")
    speak_live(f"{user_name}, here is a link you can follow: {url}")
    st.session_state.last_link = url


# ---------- QUERY HANDLER ----------
def handle_query(user_input: str, user_name: str) -> bool:
    if user_input.lower() == "exit":
        speak_live(f"Goodbye {user_name}! Have a great day!")
        return False

    text = user_input.lower()
    if "hello" in text or "hi" in text:
        speak_live(f"Hello {user_name}! How can I assist you today?")
    elif "how are you" in text:
        speak_live(f"I am doing well, thank you {user_name}! How can I assist you today?")
    elif "what is your name" in text or "your name" in text:
        speak_live("My name is Azile, your virtual assistant.")
    elif "who created you" in text or "creator" in text:
        speak_live("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in text or "capabilities" in text:
        speak_live(
            "I can answer simple questions, tell you the time and date, "
            "tell jokes, perform basic calculations, open websites, and more."
        )
    elif "help" in text or "assist" in text:
        speak_live(HELP_TEXT)
    elif "time" in text:
        tell_time(user_name)
    elif "date" in text:
        tell_date(user_name)
    elif "joke" in text:
        tell_joke(user_name)
    elif text.startswith("calculate"):
        calculate(user_input, user_name)
    elif "search" in text or "open" in text:
        open_website(user_input, user_name)
    else:
        speak_live(f"Sorry {user_name}, I don't understand that yet. {HELP_TEXT}")

    return True


# ---------- MAIN APP ----------
def main() -> None:
    # initialise session state
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None
    if "last_link" not in st.session_state:
        st.session_state.last_link = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    # Sidebar: dark/light mode selection
    mode = st.sidebar.radio("Select Theme", ["Light", "Dark"])
    if mode == "Dark":
        st.markdown(
            "<style>body{background-color:#111;color:white}</style>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<style>body{background-color:white;color:black}</style>", unsafe_allow_html=True
        )

    st.title("Azile – Virtual Assistant 🤖")

    # Ask user name if not provided
    if st.session_state.user_name is None:
        st.session_state.user_name = st.text_input("Please enter your name:", "")
        if not st.session_state.user_name:
            return
        speak_live(f"Welcome {st.session_state.user_name}! How can I assist you today?")

    # Display chat
    for who, msg in st.session_state.chat:
        st.markdown(f"**{who}:** {msg}")

    # User input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(f"{st.session_state.user_name}:")
        send = st.form_submit_button("Send")

        if send and user_input:
            st.session_state.chat.append((st.session_state.user_name, user_input))
            cont = handle_query(user_input.strip(), st.session_state.user_name)
            if not cont:
                st.session_state.chat.append(("Assistant", "Session ended."))

    # Play audio
    if st.session_state.last_audio:
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{st.session_state.last_audio}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    # Show link if generated
    if st.session_state.last_link:
        st.markdown(f"[Open this link]({st.session_state.last_link})")

    # Clear chat button
    if st.button("Clear history"):
        st.session_state.chat = []
        st.session_state.last_audio = None
        st.session_state.last_link = None


if __name__ == "__main__":
    main()
import random
import base64
from datetime import datetime
from io import BytesIO

import streamlit as st

# Safe import for gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed, audio will not work.")


HELP_TEXT = (
    "You can ask me about the time or the date, tell me to calculate something "
    "(for example: calculate 3+4), ask for a joke, or search/open a website by "
    "saying 'search' or 'open' followed by the query.  "
    "You can also say hello, ask for my name/creator, or just type 'exit' to quit."
)


# ---------- SPEAK ----------
def speak(text: str) -> None:
    st.session_state.chat.append(("Assistant", text))
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
def tell_time() -> None:
    speak(f"The current time is {datetime.now():%H:%M:%S}.")


def tell_date() -> None:
    speak(f"Today is {datetime.now():%A, %B %d, %Y}.")


def tell_joke() -> None:
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why don't scientists trust atoms? Because they make up everything.",
        "I would tell you a construction pun, but I'm still working on it.",
    ]
    speak(random.choice(jokes))


def calculate(user_input: str) -> None:
    expr = user_input.partition("calculate")[2].strip()
    try:
        # Safe eval without builtins
        result = eval(expr, {"__builtins__": None}, {})
        speak(f"The result is {result}.")
    except Exception:
        speak("Sorry, I couldn't calculate that.")


def open_website(user_input: str) -> None:
    if "youtube" in user_input:
        url = "https://www.youtube.com"
    elif "google" in user_input:
        url = "https://www.google.com"
    else:
        query = user_input.replace("search", "").replace("open", "").strip()
        url = "https://www.google.com/search?q=" + query.replace(" ", "+")
    speak(f"Here is a link you can follow: {url}")
    st.session_state.last_link = url


# ---------- QUERY HANDLER ----------
def handle_query(user_input: str) -> bool:
    if user_input == "exit":
        speak("Goodbye! Have a great day!")
        return False

    if "hello" in user_input or "hi" in user_input:
        speak("Hello! How can I assist you today?")
    elif "how are you" in user_input:
        speak("I am doing well, thank you! How can I assist you today?")
    elif "what is your name" in user_input or "your name" in user_input:
        speak("My name is Azile, your virtual assistant.")
    elif "who created you" in user_input or "creator" in user_input:
        speak("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in user_input or "capabilities" in user_input:
        speak(
            "I can answer simple questions, tell you the time and date, "
            "tell jokes, perform basic calculations, open websites, and more."
        )
    elif user_input == "help" or "assist" in user_input:
        speak(HELP_TEXT)
    elif "time" in user_input:
        tell_time()
    elif "date" in user_input:
        tell_date()
    elif "joke" in user_input:
        tell_joke()
    elif user_input.startswith("calculate"):
        calculate(user_input)
    elif "search" in user_input or "open" in user_input:
        open_website(user_input)
    else:
        speak("Sorry, I don't understand that yet. " + HELP_TEXT)

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

    st.title("Azile – Virtual Assistant - Developed by Saadman Sakib")

    # simple animated banner using emojis
    st.markdown(
        "<marquee behavior='alternate' scrollamount='8' style='font-size:24px;'>"
        "🤖💬 Azile is ready to chat! 🎉✨"
        "</marquee>",
        unsafe_allow_html=True,
    )

    st.write(HELP_TEXT)

    # display past conversation
    for who, msg in st.session_state.chat:
        st.markdown(f"**{who}:** {msg}")

    # user input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:")
        send = st.form_submit_button("Send")

        if send and user_input:
            st.session_state.chat.append(("You", user_input))
            cont = handle_query(user_input.lower().strip())
            if not cont:
                st.session_state.chat.append(("Assistant", "Session ended."))

    # autoplay audio if one was generated
    if st.session_state.last_audio:
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{st.session_state.last_audio}"
                    type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    # show link if one was generated
    if st.session_state.last_link:
        st.markdown(f"[Open this link]({st.session_state.last_link})")

    # clear history button
    if st.button("Clear history"):
        st.session_state.chat = []
        st.session_state.last_audio = None
        st.session_state.last_link = None


if __name__ == "__main__":
    main()
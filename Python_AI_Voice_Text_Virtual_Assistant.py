import random
from datetime import datetime
from io import BytesIO
import base64
import streamlit as st
import requests

st.set_page_config(page_title="Azile – Virtual Assistant", page_icon="🤖", layout="centered")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed, audio will not work.")

try:
    import geocoder
except ModuleNotFoundError:
    geocoder = None

HELP_TEXT = (
    "You can ask me about the time, date, calculations, jokes, or smart questions.\n"
    "Smart questions you can ask:\n"
    "- 'What is my country?'\n"
    "- 'Current world situation?'\n"
    "- 'What is the weather?'\n"
    "- 'Search: <topic>'\n"
    "- 'News'\n"
    "Health: depression, anxiety, stress, not feeling good, medicine info.\n"
    "General: hello, how are you, help.\n"
    "Type 'exit' to quit."
)

# ── Location & time helpers ────────────────────────────────────────────────────
def get_location_info():
    """Returns (city, country, timezone, lat, lon) using IP geolocation."""
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        data = r.json()
        return {
            "city": data.get("city", "Unknown"),
            "country": data.get("country_name", "Unknown"),
            "timezone": data.get("timezone", "UTC"),
            "lat": data.get("latitude", 0),
            "lon": data.get("longitude", 0),
            "ip": data.get("ip", ""),
        }
    except Exception:
        return None

def get_local_time():
    """Get current local time based on IP location."""
    try:
        from zoneinfo import ZoneInfo
        info = get_location_info()
        if info and info["timezone"]:
            tz = ZoneInfo(info["timezone"])
            local_now = datetime.now(tz)
            return local_now, info
    except Exception:
        pass
    return datetime.now(), None

# ── Web search / news ──────────────────────────────────────────────────────────
def web_search(query: str):
    """Search using DuckDuckGo instant answer API (no key needed)."""
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=6
        )
        data = r.json()
        abstract = data.get("AbstractText", "")
        answer = data.get("Answer", "")
        related = data.get("RelatedTopics", [])
        if answer:
            return answer
        if abstract:
            return abstract[:400]
        if related:
            for item in related[:3]:
                text = item.get("Text", "")
                if text:
                    return text[:400]
        return None
    except Exception:
        return None

def get_news():
    """Fetch top headlines from GNews (free, no key) or fallback."""
    try:
        r = requests.get(
            "https://gnews.io/api/v4/top-headlines",
            params={"lang": "en", "max": 5, "apikey": "free"},
            timeout=6
        )
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if articles:
                headlines = [f"• {a['title']}" for a in articles[:5]]
                return "\n".join(headlines)
    except Exception:
        pass
    # Fallback: DuckDuckGo news search
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": "top news today", "format": "json", "no_html": 1},
            timeout=6
        )
        data = r.json()
        topics = data.get("RelatedTopics", [])
        headlines = []
        for t in topics[:5]:
            text = t.get("Text", "")
            if text:
                headlines.append(f"• {text[:120]}")
        if headlines:
            return "\n".join(headlines)
    except Exception:
        pass
    return None

def get_weather(city=None, lat=None, lon=None):
    """Fetch weather using Open-Meteo (completely free, no key needed)."""
    try:
        if not lat or not lon:
            info = get_location_info()
            if info:
                lat, lon = info["lat"], info["lon"]
                city = info["city"]
        if not lat or not lon:
            return None, None
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "relativehumidity_2m",
            },
            timeout=6
        )
        data = r.json()
        cw = data.get("current_weather", {})
        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        code = cw.get("weathercode", 0)
        desc_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
            55: "Heavy drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
            95: "Thunderstorm", 99: "Thunderstorm with hail",
        }
        desc = desc_map.get(code, "Unknown")
        return f"{desc}, {temp}°C, wind {wind} km/h", city
    except Exception:
        return None, None

# ── Health & Pharma knowledge ──────────────────────────────────────────────────
HEALTH_KNOWLEDGE = {
    "depression": (
        "Depression is a common but serious mood disorder. Symptoms include persistent sadness, "
        "loss of interest in activities, fatigue, changes in sleep/appetite, difficulty concentrating, "
        "and feelings of worthlessness.\n\n"
        "Self-care tips:\n"
        "• Talk to someone you trust — don't isolate yourself.\n"
        "• Maintain a routine: wake up, eat, and sleep at regular times.\n"
        "• Get light exercise daily — even a 10-minute walk helps.\n"
        "• Limit alcohol and avoid recreational drugs.\n"
        "• Practice mindfulness or deep breathing.\n"
        "• Journaling your thoughts can bring clarity.\n\n"
        "⚠️ If you feel hopeless or have thoughts of self-harm, please reach out to a mental health professional immediately. "
        "You can also call a crisis helpline — you are not alone."
    ),
    "anxiety": (
        "Anxiety involves excessive worry, fear, or nervousness that interferes with daily life.\n\n"
        "Self-care tips:\n"
        "• Practice deep breathing: inhale 4 seconds, hold 4, exhale 4.\n"
        "• Limit caffeine and sugar which can worsen anxiety.\n"
        "• Ground yourself with the 5-4-3-2-1 technique: name 5 things you see, 4 you hear, 3 you can touch.\n"
        "• Regular sleep and exercise greatly reduce anxiety.\n"
        "• Avoid overthinking by writing worries down and setting a 'worry time'.\n\n"
        "⚠️ Persistent anxiety should be evaluated by a doctor."
    ),
    "stress": (
        "Stress is your body's reaction to pressure or demands. Chronic stress can harm your health.\n\n"
        "Self-care tips:\n"
        "• Identify the source of stress and address what you can control.\n"
        "• Take regular breaks — even 5 minutes away from a task helps.\n"
        "• Exercise releases endorphins which naturally reduce stress.\n"
        "• Connect with friends and family.\n"
        "• Try progressive muscle relaxation or guided meditation.\n"
        "• Prioritize tasks and say no when overwhelmed."
    ),
    "not feeling good": (
        "Feeling unwell can have many causes — physical, emotional, or both.\n\n"
        "General self-care:\n"
        "• Rest and stay hydrated — drink plenty of water.\n"
        "• Eat light, nutritious food (soups, fruits, vegetables).\n"
        "• Check your temperature for fever.\n"
        "• If it's emotional, try to name what you're feeling — sometimes just identifying it helps.\n"
        "• Avoid screens before bed and get proper sleep.\n\n"
        "⚠️ If symptoms persist more than 2-3 days or are severe, consult a doctor."
    ),
    "headache": (
        "Common headache causes: dehydration, stress, poor posture, eye strain, lack of sleep.\n\n"
        "Self-care:\n"
        "• Drink 2 glasses of water immediately.\n"
        "• Rest in a quiet, dark room.\n"
        "• Apply a cold or warm compress to your forehead or neck.\n"
        "• OTC options: Paracetamol (500mg-1g), Ibuprofen (400mg with food).\n\n"
        "⚠️ See a doctor if headache is sudden/severe, or accompanied by vision changes or stiff neck."
    ),
    "fever": (
        "Fever is a body temperature above 38°C (100.4°F) — usually a sign your immune system is fighting infection.\n\n"
        "Self-care:\n"
        "• Stay hydrated — water, oral rehydration salts, or clear broths.\n"
        "• Rest and keep cool — light clothing, ventilated room.\n"
        "• Paracetamol (500mg-1g every 4-6 hours) or Ibuprofen (400mg every 6-8 hours with food).\n"
        "• Lukewarm sponge bath can help bring temperature down.\n\n"
        "⚠️ Seek medical attention if fever exceeds 39.5°C, lasts more than 3 days, or is in an infant under 3 months."
    ),
    "cold": (
        "Common cold symptoms: runny nose, sore throat, sneezing, mild fever, fatigue.\n\n"
        "Self-care:\n"
        "• Rest as much as possible.\n"
        "• Drink warm fluids: water, honey-lemon tea, broth.\n"
        "• Steam inhalation helps with congestion.\n"
        "• OTC options: Antihistamines (Loratadine/Cetirizine) for runny nose, Paracetamol for aches/fever.\n"
        "• Zinc lozenges may shorten cold duration.\n\n"
        "⚠️ Antibiotics do NOT work on colds (they're viral). See a doctor if symptoms worsen after 7 days."
    ),
    "paracetamol": (
        "Paracetamol (Acetaminophen) — Common brand: Panadol, Tylenol, Calpol\n\n"
        "Uses: Pain relief, fever reduction.\n"
        "Adult dose: 500mg-1g every 4-6 hours. Max 4g/day.\n"
        "Child dose: Based on weight — consult label or pharmacist.\n"
        "Onset: ~30-60 minutes. Duration: 4-6 hours.\n\n"
        "⚠️ Do NOT exceed 4g/day. Overdose can cause serious liver damage. "
        "Avoid if you have liver disease or drink alcohol regularly."
    ),
    "ibuprofen": (
        "Ibuprofen — Common brands: Brufen, Advil, Nurofen\n\n"
        "Uses: Pain, fever, inflammation (headaches, muscle pain, arthritis, menstrual cramps).\n"
        "Adult dose: 200-400mg every 6-8 hours with food. Max 1200mg/day OTC.\n"
        "Onset: ~30 minutes. Duration: 6-8 hours.\n\n"
        "⚠️ Take with food to protect stomach. Avoid if you have kidney disease, stomach ulcers, or are pregnant. "
        "Do not combine with other NSAIDs."
    ),
    "antibiotic": (
        "Antibiotics are medicines that fight bacterial infections — they do NOT work on viruses (colds, flu, COVID).\n\n"
        "Common types:\n"
        "• Amoxicillin — throat, ear, chest infections.\n"
        "• Azithromycin — respiratory, skin infections.\n"
        "• Metronidazole — dental, gut infections.\n"
        "• Ciprofloxacin — urinary tract, gut infections.\n\n"
        "⚠️ Always complete the full course even if you feel better. "
        "Never take antibiotics without a prescription — antibiotic resistance is a serious global health threat."
    ),
    "sleep": (
        "Poor sleep affects mood, immunity, and concentration.\n\n"
        "Sleep hygiene tips:\n"
        "• Stick to a consistent sleep schedule — even on weekends.\n"
        "• Avoid screens 1 hour before bed (blue light disrupts melatonin).\n"
        "• Keep your room cool, dark, and quiet.\n"
        "• Avoid caffeine after 2pm.\n"
        "• Try a relaxing pre-sleep routine: reading, light stretching, or meditation.\n"
        "• Melatonin (0.5-3mg) can help for short-term sleep issues — consult a pharmacist.\n\n"
        "⚠️ Chronic insomnia lasting more than a month should be evaluated by a doctor."
    ),
    "first aid": (
        "Basic first aid reminders:\n\n"
        "🩹 Cuts/Wounds: Clean with water, apply pressure to stop bleeding, cover with a clean bandage.\n"
        "🔥 Burns: Cool under running water for 20 minutes. Do NOT use ice or butter.\n"
        "🫁 Choking: Give 5 back blows between shoulder blades, then 5 abdominal thrusts (Heimlich).\n"
        "💊 Poisoning: Do NOT induce vomiting. Call emergency services immediately.\n"
        "🤕 Fainting: Lay person flat, elevate legs, loosen tight clothing.\n"
        "🫀 CPR: 30 chest compressions + 2 rescue breaths. Call emergency services first.\n\n"
        "⚠️ Always call emergency services (999/911/112) for serious emergencies."
    ),
}

def get_health_response(text: str):
    for keyword, response in HEALTH_KNOWLEDGE.items():
        if keyword in text:
            return response
    return None

# ── Autoplay audio ─────────────────────────────────────────────────────────────
def autoplay_audio(audio_bytes: bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    unique_id = random.randint(100000, 999999)
    st.components.v1.html(f"""
        <audio id="azile_audio_{unique_id}" autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var a = document.getElementById("azile_audio_{unique_id}");
            if (a) a.play().catch(function(e) {{ console.log("Autoplay blocked:", e); }});
        </script>
    """, height=0)

# ── Speak ──────────────────────────────────────────────────────────────────────
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

# ── Features ───────────────────────────────────────────────────────────────────
def tell_time():
    local_now, info = get_local_time()
    if info:
        speak(f"The current local time in {info['city']}, {info['country']} is {local_now:%H:%M:%S} ({info['timezone']}).")
    else:
        speak(f"The current time is {datetime.now():%H:%M:%S}.")

def tell_date():
    local_now, info = get_local_time()
    if info:
        speak(f"Today is {local_now:%A, %B %d, %Y} in {info['city']}, {info['country']}.")
    else:
        speak(f"Today is {datetime.now():%A, %B %d, %Y}.")

def tell_joke():
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why don't scientists trust atoms? Because they make up everything.",
        "I would tell you a construction pun, but I'm still working on it.",
        "What do you call fake spaghetti? An impasta!",
        "Why did the bicycle fall over? Because it was two-tired.",
    ]
    speak(random.choice(jokes))

def calculate(user_input: str):
    expr = user_input.partition("calculate")[2].strip()
    try:
        result = eval(expr, {"__builtins__": None}, {})
        speak(f"The result of {expr} is {result}.")
    except Exception:
        speak("Sorry, I couldn't calculate that. Please try something like: calculate 10 * 5")

def my_country():
    info = get_location_info()
    if info:
        speak(f"Based on your IP address, you appear to be in {info['city']}, {info['country']}.")
    else:
        speak("Sorry, I could not detect your location right now.")

def world_situation():
    news = get_news()
    if news:
        speak(f"Here are today's top headlines:\n{news}")
    else:
        speak("The world situation is constantly evolving. Please follow reliable news sources like BBC, Reuters, or Al Jazeera for the latest updates.")

def weather_info():
    result, city = get_weather()
    if result:
        speak(f"Current weather in {city}: {result}.")
    else:
        speak("Sorry, I couldn't fetch the weather right now. Please try again later.")

def search_web(query: str):
    speak(f"Let me search for: {query}")
    result = web_search(query)
    if result:
        speak(result)
    else:
        speak(f"I couldn't find a direct answer for '{query}'. Try searching on Google, Wikipedia, or BBC.")

# ── Query handler ──────────────────────────────────────────────────────────────
def handle_query(user_input: str) -> bool:
    text = user_input.lower()

    if text == "exit":
        speak("Goodbye! Have a great day!"); return False
    elif "hello" in text or "hi" in text or "hey" in text:
        speak("Hello! How can I assist you today?")
    elif "how are you" in text:
        speak("I am doing well, thank you! How can I assist you today?")
    elif "what is your name" in text or "your name" in text:
        speak("My name is Azile, your virtual assistant.")
    elif "who created you" in text or "creator" in text:
        speak("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in text or "capabilities" in text:
        speak("I can answer questions, tell time and date by your location, check the weather, search the web, get news, tell jokes, do calculations, give health and medicine advice, and more!")
    elif "help" in text:
        speak(HELP_TEXT)

    # Time & date
    elif "time" in text:
        tell_time()
    elif "date" in text or "today" in text:
        tell_date()

    # Weather
    elif "weather" in text or "temperature" in text or "forecast" in text:
        weather_info()

    # News
    elif "news" in text or "headlines" in text or "world situation" in text or "current situation" in text:
        world_situation()

    # Web search
    elif text.startswith("search:") or text.startswith("search "):
        query = text.replace("search:", "").replace("search ", "", 1).strip()
        search_web(query)

    # Jokes & math
    elif "joke" in text:
        tell_joke()
    elif text.startswith("calculate") or "what is" in text and any(op in text for op in ["+", "-", "*", "/"]):
        calculate(user_input)

    # Location
    elif "country" in text or "location" in text or "where am i" in text or "city" in text:
        my_country()

    # Health & pharma — check knowledge base first
    else:
        health_resp = get_health_response(text)
        if health_resp:
            speak(health_resp)
        # Catch-all mental health / not feeling well
        elif any(w in text for w in ["sad", "lonely", "hopeless", "worthless", "crying", "cry", "pain", "hurt", "suffering"]):
            speak(
                "I'm really sorry you're feeling this way. You're not alone, and it's okay to not be okay sometimes.\n\n"
                "Please consider:\n"
                "• Talking to someone you trust — a friend, family member, or counselor.\n"
                "• Taking a few slow, deep breaths right now.\n"
                "• Being gentle with yourself — you don't have to have everything figured out.\n\n"
                "If things feel very dark, please reach out to a mental health crisis line in your country. "
                "You deserve support and care. 💙"
            )
        elif any(w in text for w in ["tired", "exhausted", "burnout", "burnt out", "overwhelmed"]):
            speak(
                "It sounds like you're running low on energy. That's completely valid.\n\n"
                "Try to:\n"
                "• Take a short break — even 10 minutes outside.\n"
                "• Drink some water and eat something nourishing.\n"
                "• Say no to one thing today that isn't urgent.\n"
                "• Rest without guilt — rest is productive.\n\n"
                "You're doing better than you think. 🌿"
            )
        else:
            speak("Sorry, I don't understand that yet. Try 'help' to see what I can do, or use 'search: <topic>' to look something up.")

    return True

# ── Session init ───────────────────────────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# ── Theme ──────────────────────────────────────────────────────────────────────
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])
is_dark = theme == "Dark"

bg          = "#111111" if is_dark else "#ffffff"
fg          = "#f0f0f0" if is_dark else "#111111"
sidebar_bg  = "#1a1a1a" if is_dark else "#f5f5f5"
chat_bg     = "#1e1e1e" if is_dark else "#f9f9f9"
chat_border = "#333333" if is_dark else "#dddddd"
input_bg    = "#2a2a2a" if is_dark else "#ffffff"
input_bdr   = "#555555" if is_dark else "#cccccc"
btn_bg      = "#333333" if is_dark else "#eeeeee"
btn_bdr     = "#555555" if is_dark else "#cccccc"

st.markdown(f"""
<style>
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
section.main {{ background-color: {bg} !important; color: {fg} !important; }}

[data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
[data-testid="stSidebar"] * {{ color: {fg} !important; background-color: transparent !important; }}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] label,
[data-testid="stMain"] li,
.stMarkdown, .stMarkdown * {{ color: {fg} !important; }}

.chat-box {{
    background-color: {chat_bg} !important;
    border: 1px solid {chat_border} !important;
    border-radius: 10px;
    padding: 16px;
    height: 220px;
    overflow-y: auto;
    margin-bottom: 12px;
}}
.chat-box p, .chat-box strong {{ color: {fg} !important; }}

.stTextInput input {{
    background-color: {input_bg} !important;
    color: {fg} !important;
    border: 1px solid {input_bdr} !important;
    border-radius: 6px !important;
}}
.stTextInput label {{ color: {fg} !important; }}

.stButton > button,
.stFormSubmitButton > button {{
    background-color: {btn_bg} !important;
    color: {fg} !important;
    border: 1px solid {btn_bdr} !important;
    border-radius: 6px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar info ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Azile")
    st.markdown("**Virtual Assistant**")
    st.markdown("---")
    st.markdown("**Try asking:**")
    tips = [
        "What time is it?", "What's the weather?", "News",
        "Search: climate change", "Tell me a joke", "Calculate 25 * 4",
        "I have a headache", "Tell me about depression",
        "What is paracetamol?", "What is my country?",
    ]
    for t in tips:
        st.markdown(f"- {t}")
    st.markdown("---")
    st.caption("Developed by Saadman Sakib")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.title("Azile – Virtual Assistant - Developed by Saadman Sakib")
st.markdown("### Introduction")
st.markdown(HELP_TEXT)

# ── Chat history ───────────────────────────────────────────────────────────────
chat_html = '<div class="chat-box" id="chat-box">'
if not st.session_state.chat:
    chat_html += '<p style="color:#888; text-align:center; margin-top:75px;">Your conversation will appear here.</p>'
else:
    for who, msg in st.session_state.chat:
        safe_msg = msg.replace("\n", "<br>")
        chat_html += f'<p><strong>{who}:</strong> {safe_msg}</p>'
chat_html += '</div>'
chat_html += '<script>var cb=document.getElementById("chat-box");if(cb)cb.scrollTop=cb.scrollHeight;</script>'
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input form ─────────────────────────────────────────────────────────────────
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

if st.session_state.last_audio:
    autoplay_audio(st.session_state.last_audio)
    st.session_state.last_audio = None

if st.button("Clear history"):
    st.session_state.chat = []
    st.session_state.last_audio = None
    st.rerun()

if __name__ == "__main__":
    pass
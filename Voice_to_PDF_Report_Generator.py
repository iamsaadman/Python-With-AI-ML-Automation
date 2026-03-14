import streamlit as st
import speech_recognition as sr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import tempfile
import time
import re
from datetime import datetime

st.set_page_config(page_title="Voice to PDF Bill", page_icon="🎤", layout="centered")

st.markdown("""
<style>
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.cursor { display:inline-block; animation:blink 1s infinite; font-weight:700; }
.tw-box {
    background:#f0f4ff;
    border-left:4px solid #4f6ef7;
    border-radius:8px;
    padding:0.9rem 1.1rem;
    margin-bottom:1rem;
    font-size:1rem;
    color:#1a1a2e;
    min-height:48px;
}
.live-box {
    background:#fff8e1;
    border:1.5px dashed #f5a623;
    border-radius:8px;
    padding:0.6rem 1rem;
    margin:0.4rem 0 0.8rem;
    font-size:0.93rem;
    color:#7a5200;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🎤 Voice to PDF Bill Generator")
st.caption("Developed by **Saadman Sakib**")
st.divider()

for k, v in {
    "items": [], "messages": [], "last_audio_id": None,
    "tw_done": False, "pending_item": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

recognizer = sr.Recognizer()

# ── Bangla digit → arabic ──
bangla_digits = {
    "০":"0","১":"1","২":"2","৩":"3","৪":"4",
    "৫":"5","৬":"6","৭":"7","৮":"8","৯":"9"
}

# ── Word-number maps ──
BANGLA_NUMS = {
    "শূন্য":0,"এক":1,"দুই":2,"দো":2,"তিন":3,"চার":4,"পাঁচ":5,
    "ছয়":6,"সাত":7,"আট":8,"নয়":9,"দশ":10,
    "এগারো":11,"বারো":12,"তেরো":13,"চৌদ্দ":14,"পনেরো":15,
    "ষোলো":16,"সতেরো":17,"আঠারো":18,"উনিশ":19,"বিশ":20,
    "একুশ":21,"বাইশ":22,"তেইশ":23,"চব্বিশ":24,"পঁচিশ":25,
    "ছাব্বিশ":26,"সাতাশ":27,"আটাশ":28,"উনত্রিশ":29,
    "ত্রিশ":30,"চল্লিশ":40,"পঞ্চাশ":50,"ষাট":60,
    "সত্তর":70,"আশি":80,"নব্বই":90,
    "একশো":100,"একশ":100,"দুইশো":200,"দুশো":200,"দুশ":200,
    "তিনশো":300,"তিনশ":300,"চারশো":400,"চারশ":400,
    "পাঁচশো":500,"পাঁচশ":500,"ছয়শো":600,"সাতশো":700,
    "আটশো":800,"নয়শো":900,
    "হাজার":1000,"একহাজার":1000,"দুইহাজার":2000,
    "পাঁচহাজার":5000,"দশহাজার":10000,
}

ENGLISH_NUMS = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10,
    "eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
    "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,
    "thirty":30,"forty":40,"fifty":50,"sixty":60,
    "seventy":70,"eighty":80,"ninety":90,
    "hundred":100,"thousand":1000,"lakh":100000,
}

STRIP_WORDS = {
    "taka","টাকা","টাকায়","মূল্য","দাম","price","amount",
    "cost","পরিমাণ","tk","bdt","and","a","the"
}

CLEAR_WORDS = {
    "clear","ক্লিয়ার","মুছো","মুছ","রিসেট","reset"
}

def conv_digits(text):
    for b, e in bangla_digits.items():
        text = text.replace(b, e)
    return text

def resolve_numwords(tokens):
    """Consume leading number-words (Bangla or English) → (num_str, rest)."""
    ALL = {}
    ALL.update(BANGLA_NUMS)
    ALL.update(ENGLISH_NUMS)
    total = 0
    current = 0
    consumed = 0
    for i, tok in enumerate(tokens):
        w = tok.strip(".,").lower()
        if w not in ALL:
            break
        v = ALL[w]
        if v >= 1000:
            current = (current if current else 1) * v
            total += current
            current = 0
        elif v >= 100:
            current = (current if current else 1) * v
        else:
            current += v
        consumed = i + 1
    if consumed:
        return str(total + current), tokens[consumed:]
    return None, tokens

def count_digits_in(text):
    """How many digit tokens (arabic or word-numbers) are in text."""
    ALL = set(BANGLA_NUMS) | set(ENGLISH_NUMS)
    count = 0
    for tok in text.split():
        w = tok.strip(".,").lower()
        if re.fullmatch(r'\d+(?:\.\d+)?', w) or w in ALL:
            count += 1
    return count

def best_transcript(audio_data):
    """
    Try en-US and bn-BD in parallel, pick the one that has more digit hits
    (meaning it correctly heard numbers). Fallback to whichever succeeded.
    """
    results = {}
    for lang in ["en-US", "bn-BD"]:
        try:
            t = recognizer.recognize_google(audio_data, language=lang)
            results[lang] = t
        except Exception:
            pass

    if not results:
        raise sr.UnknownValueError()

    if len(results) == 1:
        return list(results.values())[0]

    # Pick the transcript with more detected numbers
    en_score = count_digits_in(conv_digits(results["en-US"]))
    bn_score = count_digits_in(conv_digits(results["bn-BD"]))

    # Prefer Bangla if scores equal and text has Bangla chars
    if bn_score >= en_score and any('\u0980' <= c <= '\u09FF' for c in results["bn-BD"]):
        return results["bn-BD"]
    return results["en-US"]

def normalize(text):
    text = conv_digits(text)
    tokens = text.split()
    out = []
    for t in tokens:
        if t.lower().strip(".,/-") not in STRIP_WORDS:
            out.append(t)
    return " ".join(out)

def parse_items(raw_text):
    """
    Scan tokens left-to-right.
    Non-number words → name buffer.
    Number (digit or word) → close buffer, emit (name, price).
    Returns: (pairs_list, leftover_name_or_None)
    """
    text = normalize(raw_text)
    tokens = text.split()
    pairs = []
    name_buf = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        clean = tok.strip(".,")

        # Arabic digit
        if re.fullmatch(r'\d+(?:\.\d+)?', clean):
            pairs.append((" ".join(name_buf).strip() or None, clean))
            name_buf = []
            i += 1
            continue

        # Word number
        num_str, rest = resolve_numwords(tokens[i:])
        if num_str:
            pairs.append((" ".join(name_buf).strip() or None, num_str))
            name_buf = []
            tokens = tokens[:i] + rest
            continue

        name_buf.append(tok)
        i += 1

    leftover = " ".join(name_buf).strip() or None
    return pairs, leftover

def is_clear(text):
    return any(kw in text.lower() for kw in CLEAR_WORDS)


# ── Typewriter ──
welcome = (
    "👋 হ্যালো! আজকের বিলের সব কিছু বলুন। "
    "বাংলায় বলুন: 'চাল আশি দুধ পঞ্চাশ' "
    "অথবা English: 'Rice 80 Milk 50 Oil 120' — "
    "একসাথে বললেও আলাদা entry হবে! 🧾"
)
tw_ph = st.empty()
if not st.session_state["tw_done"]:
    buf = ""
    for ch in welcome:
        buf += ch
        tw_ph.markdown(
            f'<div class="tw-box">{buf}<span class="cursor">|</span></div>',
            unsafe_allow_html=True
        )
        time.sleep(0.018)
    st.session_state["tw_done"] = True
tw_ph.markdown(f'<div class="tw-box">{welcome}</div>', unsafe_allow_html=True)

if st.session_state["pending_item"]:
    st.info(f"⏳ **{st.session_state['pending_item']}** — এর দাম বলুন / say the price.")

for role, msg in st.session_state["messages"]:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)

audio = st.audio_input("🎙️ Tap to record — বাংলা বা English, যেকোনো ভাষায়")

if audio is not None and audio.file_id != st.session_state["last_audio_id"]:
    st.session_state["last_audio_id"] = audio.file_id

    live_ph = st.empty()
    live_ph.markdown(
        '<div class="live-box">🔴 Processing<span class="cursor">…</span></div>',
        unsafe_allow_html=True
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio.read())
        f.flush()
        with sr.AudioFile(f.name) as source:
            audio_data = recognizer.record(source)

    try:
        raw = best_transcript(audio_data)

        live_ph.markdown(
            f'<div class="live-box">🎙️ শুনলাম: <b>{raw}</b></div>',
            unsafe_allow_html=True
        )
        time.sleep(0.5)
        st.session_state["messages"].append(("user", raw))

        if is_clear(raw):
            st.session_state.update({"items": [], "pending_item": None})
            st.session_state["messages"].append(("assistant", "🗑️ তালিকা মুছে গেছে।"))

        else:
            pairs, leftover = parse_items(raw)

            # Attach pending item to first price-only pair
            if st.session_state["pending_item"]:
                if pairs:
                    fn, fp = pairs[0]
                    if not fn:
                        pairs[0] = (st.session_state["pending_item"], fp)
                st.session_state["pending_item"] = None

            added = []
            for name, price in pairs:
                if name and price:
                    st.session_state["items"].append((name, price))
                    added.append(f"✅ **{name}** — ৳ {price}")
                elif price and not name:
                    st.session_state["messages"].append(
                        ("assistant", "⚠️ দাম পেলাম কিন্তু item নাম নেই।")
                    )

            if added:
                st.session_state["messages"].append(("assistant", "\n\n".join(added)))

            if leftover:
                st.session_state["pending_item"] = leftover
                st.session_state["messages"].append(
                    ("assistant", f"📝 **{leftover}** — এর দাম বলুন / say the price.")
                )

            if not pairs and not leftover:
                st.session_state["messages"].append(
                    ("assistant", "⚠️ বুঝলাম না। চেষ্টা করুন: *'চাল ৮০'* বা *'Rice 80'*")
                )

    except sr.UnknownValueError:
        live_ph.empty()
        st.session_state["messages"].append(
            ("assistant", "⚠️ বুঝতে পারিনি। আবার চেষ্টা করুন।")
        )
    except sr.RequestError:
        live_ph.empty()
        st.session_state["messages"].append(("assistant", "❌ Network error."))

    st.rerun()

# ── Price list ──
if st.session_state["items"]:
    st.divider()
    st.subheader(f"📋 Price List — {len(st.session_state['items'])} items")
    total = 0.0
    for i, (name, price) in enumerate(st.session_state["items"], 1):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.write(f"**{i}.** {name or '—'}")
        with c2:
            st.write(f"৳ {price}")
        try:
            total += float(price)
        except ValueError:
            pass
    st.divider()
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write("**Total**")
    with c2:
        st.write(f"**৳ {total:,.0f}**")
    if st.button("🗑️ Clear All"):
        st.session_state.update({"items": [], "pending_item": None})
        st.session_state["messages"].append(("assistant", "🗑️ তালিকা মুছে গেছে।"))
        st.rerun()
else:
    st.info("কোনো item নেই — রেকর্ড শুরু করুন! 🎙️")

# ── PDF ──
def generate_pdf(items):
    buffer = BytesIO()
    w, h = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, h - 55, "Price List Report")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(50, h - 72,
        f"Generated {datetime.now().strftime('%d %b %Y  %H:%M')}  |  Developed by Saadman Sakib")
    y = h - 105
    c.setFillColorRGB(0.88, 0.88, 0.88)
    c.rect(40, y - 5, w - 80, 20, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y + 2, "#")
    c.drawString(80, y + 2, "Item")
    c.drawRightString(w - 50, y + 2, "Price (Taka)")
    y -= 22
    total = 0.0
    for i, (name, price) in enumerate(items, 1):
        if y < 80:
            c.showPage()
            y = h - 60
        if i % 2 == 0:
            c.setFillColorRGB(0.96, 0.96, 0.96)
            c.rect(40, y - 5, w - 80, 20, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        c.drawString(50, y + 2, str(i))
        c.drawString(80, y + 2, name or "—")
        c.drawRightString(w - 50, y + 2, price or "—")
        try:
            total += float(price) if price else 0
        except ValueError:
            pass
        y -= 22
    y -= 8
    c.setFillColorRGB(0.82, 0.82, 0.82)
    c.rect(40, y - 5, w - 80, 22, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(80, y + 4, "Total")
    c.drawRightString(w - 50, y + 4, f"{total:,.0f}")
    c.save()
    buffer.seek(0)
    return buffer

if st.session_state["items"]:
    pdf = generate_pdf(st.session_state["items"])
    st.download_button("📄 Download PDF", pdf, "price_list.pdf",
                       "application/pdf", use_container_width=True)
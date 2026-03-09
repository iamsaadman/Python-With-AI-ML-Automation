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

try:
    import geocoder
except ModuleNotFoundError:
    geocoder = None

HELP_TEXT = (
    "You can ask me about the time, date, calculations, jokes, or smart questions.\n"
    "Smart questions you can ask:\n"
    "- 'What is my country?' | 'Weather' | 'News'\n"
    "- 'Search: <topic>'\n"
    "Health & Medicine: depression, anxiety, paracetamol, amoxicillin, diabetes, asthma...\n"
    "General: hello, how are you, help. | Type 'exit' to quit."
)

# ── Location & time ────────────────────────────────────────────────────────────
def get_location_info():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        data = r.json()
        return {"city": data.get("city","Unknown"), "country": data.get("country_name","Unknown"),
                "timezone": data.get("timezone","UTC"), "lat": data.get("latitude",0), "lon": data.get("longitude",0)}
    except Exception:
        return None

def get_local_time():
    try:
        from zoneinfo import ZoneInfo
        info = get_location_info()
        if info and info["timezone"]:
            return datetime.now(ZoneInfo(info["timezone"])), info
    except Exception:
        pass
    return datetime.now(), None

# ── Web helpers ────────────────────────────────────────────────────────────────
def web_search(query):
    try:
        r = requests.get("https://api.duckduckgo.com/", params={"q":query,"format":"json","no_html":1,"skip_disambig":1}, timeout=6)
        data = r.json()
        for key in ["Answer","AbstractText"]:
            val = data.get(key,"")
            if val: return val[:400]
        for item in data.get("RelatedTopics",[])[:3]:
            t = item.get("Text","")
            if t: return t[:400]
    except Exception:
        pass
    return None

def get_news():
    try:
        r = requests.get("https://api.duckduckgo.com/", params={"q":"top news today","format":"json","no_html":1}, timeout=6)
        topics = r.json().get("RelatedTopics",[])
        lines = [f"• {t.get('Text','')[:120]}" for t in topics[:5] if t.get("Text")]
        if lines: return "\n".join(lines)
    except Exception:
        pass
    return None

def get_weather():
    try:
        info = get_location_info()
        if not info: return None, None
        r = requests.get("https://api.open-meteo.com/v1/forecast",
            params={"latitude":info["lat"],"longitude":info["lon"],"current_weather":True}, timeout=6)
        cw = r.json().get("current_weather",{})
        desc_map = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",
            51:"Light drizzle",61:"Slight rain",63:"Rain",65:"Heavy rain",71:"Slight snow",
            73:"Snow",80:"Rain showers",95:"Thunderstorm"}
        desc = desc_map.get(cw.get("weathercode",0),"Unknown")
        return f"{desc}, {cw.get('temperature')}°C, wind {cw.get('windspeed')} km/h", info["city"]
    except Exception:
        return None, None

# ══════════════════════════════════════════════════════════════════════════════
# VAST PHARMACEUTICAL & HEALTH KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════
HEALTH_KNOWLEDGE = {

    # ── MENTAL HEALTH ─────────────────────────────────────────────────────────
    "depression": (
        "🧠 DEPRESSION — Overview & Self-Care\n\n"
        "Depression is a serious mood disorder affecting how you feel, think, and handle daily activities.\n\n"
        "Symptoms: Persistent sadness, loss of interest, fatigue, sleep changes, appetite changes, "
        "difficulty concentrating, feelings of worthlessness, thoughts of death or suicide.\n\n"
        "Types:\n"
        "• Major Depressive Disorder (MDD) — severe episodes lasting 2+ weeks.\n"
        "• Persistent Depressive Disorder (Dysthymia) — chronic low mood for 2+ years.\n"
        "• Seasonal Affective Disorder (SAD) — triggered by seasonal changes.\n"
        "• Postpartum Depression — after childbirth.\n"
        "• Bipolar Depression — depressive episodes within bipolar disorder.\n\n"
        "Self-care:\n"
        "• Maintain a daily routine — structure reduces overwhelm.\n"
        "• Exercise 30 min/day — releases serotonin and endorphins naturally.\n"
        "• Eat a balanced diet — omega-3s (fish, walnuts) support brain health.\n"
        "• Limit alcohol — it's a depressant that worsens symptoms.\n"
        "• Social connection — even a short call helps.\n"
        "• Mindfulness and CBT (Cognitive Behavioural Therapy) techniques.\n"
        "• Sleep hygiene — consistent sleep times are critical.\n\n"
        "Medical treatment:\n"
        "• SSRIs (first-line): Fluoxetine, Sertraline, Escitalopram.\n"
        "• SNRIs: Venlafaxine, Duloxetine.\n"
        "• Therapy: CBT, IPT (Interpersonal Therapy), psychodynamic therapy.\n\n"
        "⚠️ If you have thoughts of self-harm or suicide, please contact a crisis helpline immediately. You are not alone. 💙"
    ),
    "anxiety": (
        "🧠 ANXIETY — Overview & Self-Care\n\n"
        "Anxiety is excessive, persistent worry or fear that interferes with daily life.\n\n"
        "Types:\n"
        "• Generalised Anxiety Disorder (GAD) — constant worry about everyday things.\n"
        "• Panic Disorder — sudden intense panic attacks.\n"
        "• Social Anxiety Disorder — fear of social situations.\n"
        "• Phobias — intense fear of specific things.\n"
        "• OCD, PTSD — anxiety-related conditions.\n\n"
        "Symptoms: Racing heart, sweating, trembling, shortness of breath, feeling of dread, insomnia.\n\n"
        "Self-care:\n"
        "• Box breathing: inhale 4s → hold 4s → exhale 4s → hold 4s. Repeat.\n"
        "• 5-4-3-2-1 grounding: 5 things you see, 4 hear, 3 touch, 2 smell, 1 taste.\n"
        "• Limit caffeine, sugar, and alcohol.\n"
        "• Exercise daily — one of the most effective natural anxiety reducers.\n"
        "• Progressive Muscle Relaxation (PMR) — tense and release each muscle group.\n"
        "• Challenge negative thoughts — ask 'Is this thought realistic?'\n\n"
        "Medical treatment:\n"
        "• SSRIs/SNRIs (long-term): Sertraline, Escitalopram, Venlafaxine.\n"
        "• Buspirone — non-addictive anti-anxiety.\n"
        "• Benzodiazepines (short-term only): Diazepam, Lorazepam — risk of dependence.\n"
        "• Beta-blockers (Propranolol) for situational anxiety (e.g. public speaking).\n"
        "• CBT is highly effective — consider therapy.\n\n"
        "⚠️ Do not self-medicate with benzodiazepines — consult a doctor."
    ),
    "stress": (
        "🧠 STRESS — Management & Self-Care\n\n"
        "Stress is your body's natural fight-or-flight response to demands or threats. "
        "Chronic stress damages the immune system, heart, and mental health.\n\n"
        "Signs of chronic stress: Headaches, muscle tension, fatigue, irritability, "
        "sleep problems, digestive issues, low immunity.\n\n"
        "Self-care:\n"
        "• Identify stressors — write them down and separate controllable vs uncontrollable.\n"
        "• Time management — prioritise tasks, break large tasks into small steps.\n"
        "• Physical exercise — 20-30 min daily lowers cortisol significantly.\n"
        "• Mindfulness meditation — even 10 min/day shows measurable benefits.\n"
        "• Social support — talk to friends, family, or a counsellor.\n"
        "• Hobbies and leisure — protect time for activities you enjoy.\n"
        "• Limit news and social media consumption.\n"
        "• Adequate sleep — 7-9 hours per night.\n\n"
        "⚠️ If stress leads to burnout, panic attacks, or physical symptoms, see a doctor."
    ),
    "bipolar": (
        "🧠 BIPOLAR DISORDER\n\n"
        "Bipolar disorder causes extreme mood swings — manic highs and depressive lows.\n\n"
        "Types:\n"
        "• Bipolar I — full manic episodes lasting 7+ days, depressive episodes.\n"
        "• Bipolar II — hypomanic episodes (less severe) and major depression.\n"
        "• Cyclothymia — milder mood swings over 2+ years.\n\n"
        "Manic symptoms: Elevated mood, reduced need for sleep, racing thoughts, impulsivity, grandiosity.\n"
        "Depressive symptoms: See depression section.\n\n"
        "Medications:\n"
        "• Mood stabilisers: Lithium (gold standard), Valproate, Lamotrigine, Carbamazepine.\n"
        "• Atypical antipsychotics: Quetiapine, Olanzapine, Aripiprazole.\n"
        "• Antidepressants are used cautiously — can trigger mania if used alone.\n\n"
        "⚠️ Bipolar disorder requires lifelong management. Never stop medication without consulting your psychiatrist."
    ),
    "schizophrenia": (
        "🧠 SCHIZOPHRENIA\n\n"
        "Schizophrenia is a chronic brain disorder affecting thinking, feeling, and behaviour.\n\n"
        "Symptoms:\n"
        "• Positive: Hallucinations, delusions, disorganised thinking/speech.\n"
        "• Negative: Flat affect, social withdrawal, reduced motivation, poor hygiene.\n"
        "• Cognitive: Memory issues, difficulty concentrating.\n\n"
        "Medications (Antipsychotics):\n"
        "• Typical: Haloperidol, Chlorpromazine — effective but more side effects.\n"
        "• Atypical (preferred): Risperidone, Olanzapine, Quetiapine, Clozapine (treatment-resistant).\n"
        "• Clozapine requires regular blood monitoring (risk of agranulocytosis).\n\n"
        "⚠️ Must be managed by a psychiatrist. Do not stop medication abruptly — risk of relapse is high."
    ),
    "adhd": (
        "🧠 ADHD — Attention Deficit Hyperactivity Disorder\n\n"
        "ADHD affects attention, impulse control, and activity levels.\n\n"
        "Symptoms:\n"
        "• Inattentive type: Difficulty focusing, forgetfulness, losing things, easily distracted.\n"
        "• Hyperactive-impulsive type: Fidgeting, interrupting, excessive talking, risk-taking.\n"
        "• Combined type: Both above.\n\n"
        "Medications:\n"
        "• Stimulants (first-line): Methylphenidate (Ritalin, Concerta), Amphetamine salts (Adderall).\n"
        "• Non-stimulants: Atomoxetine (Strattera), Guanfacine, Clonidine.\n\n"
        "Self-management:\n"
        "• Use planners, calendars, timers, and checklists.\n"
        "• Break tasks into small steps. Use the Pomodoro technique (25 min work, 5 min break).\n"
        "• Regular exercise significantly improves focus.\n"
        "• Reduce sugar and processed foods.\n\n"
        "⚠️ ADHD medications are controlled substances — only use as prescribed."
    ),
    "ptsd": (
        "🧠 PTSD — Post-Traumatic Stress Disorder\n\n"
        "PTSD develops after experiencing or witnessing traumatic events.\n\n"
        "Symptoms: Flashbacks, nightmares, severe anxiety, emotional numbness, hypervigilance, avoidance.\n\n"
        "Treatments:\n"
        "• Trauma-focused CBT — gold standard therapy.\n"
        "• EMDR (Eye Movement Desensitisation and Reprocessing).\n"
        "• Medications: SSRIs (Sertraline, Paroxetine), Prazosin (for nightmares).\n\n"
        "Self-care:\n"
        "• Grounding techniques during flashbacks.\n"
        "• Safe social connections.\n"
        "• Regular routine and physical exercise.\n"
        "• Avoid alcohol and substances.\n\n"
        "⚠️ Please seek professional support — PTSD is very treatable with proper care."
    ),

    # ── PAIN & FEVER ──────────────────────────────────────────────────────────
    "paracetamol": (
        "💊 PARACETAMOL (Acetaminophen)\n"
        "Brands: Panadol, Tylenol, Calpol, Disprol, Tempra\n\n"
        "Class: Analgesic / Antipyretic\n"
        "Uses: Mild-moderate pain (headache, toothache, back pain, period pain), fever.\n\n"
        "Dosage:\n"
        "• Adults: 500mg–1g every 4–6 hours. Max 4g/day.\n"
        "• Children (6–12 yrs): 250–500mg every 4–6 hours.\n"
        "• Children (1–5 yrs): 120–250mg every 4–6 hours.\n"
        "• Elderly: Max 3g/day recommended.\n\n"
        "Onset: 30–60 min. Duration: 4–6 hours.\n\n"
        "Interactions: Warfarin (increases bleeding risk at high doses), alcohol (liver risk).\n\n"
        "Side effects (rare at normal doses): Liver damage with overdose, skin rash.\n\n"
        "⚠️ CRITICAL: Do NOT exceed 4g/day. Overdose causes severe, potentially fatal liver damage. "
        "Avoid with liver disease or heavy alcohol use. Seek emergency care immediately if overdose suspected."
    ),
    "ibuprofen": (
        "💊 IBUPROFEN\n"
        "Brands: Brufen, Advil, Nurofen, Calprofen\n\n"
        "Class: NSAID (Non-Steroidal Anti-Inflammatory Drug)\n"
        "Uses: Pain, fever, inflammation — headaches, muscle/joint pain, arthritis, menstrual cramps, dental pain.\n\n"
        "Dosage:\n"
        "• Adults: 200–400mg every 6–8 hours with food. Max 1200mg/day OTC (2400mg prescription).\n"
        "• Children: Weight-based — 5–10mg/kg every 6–8 hours.\n\n"
        "Onset: 20–30 min. Duration: 6–8 hours.\n\n"
        "Interactions: Aspirin, Warfarin, ACE inhibitors, diuretics, Lithium, SSRIs.\n\n"
        "Side effects: GI upset, nausea, heartburn, dizziness. Long-term: stomach ulcers, kidney damage.\n\n"
        "⚠️ Always take with food. Avoid in: peptic ulcers, kidney/liver disease, third trimester pregnancy, "
        "heart failure, elderly with dehydration. Do NOT combine with other NSAIDs."
    ),
    "aspirin": (
        "💊 ASPIRIN (Acetylsalicylic Acid)\n"
        "Brands: Disprin, Bayer Aspirin, Ecotrin\n\n"
        "Class: NSAID / Antiplatelet\n"
        "Uses:\n"
        "• Low dose (75–100mg/day): Blood thinner — prevents heart attacks and strokes.\n"
        "• Standard dose (300–600mg): Pain relief, fever, inflammation.\n\n"
        "Dosage:\n"
        "• Antiplatelet: 75mg once daily with food.\n"
        "• Pain/fever: 300–600mg every 4–6 hours. Max 4g/day.\n\n"
        "Interactions: Warfarin, Ibuprofen, other NSAIDs, SSRIs, Methotrexate.\n\n"
        "Side effects: GI irritation, bleeding, Reye's syndrome (in children).\n\n"
        "⚠️ NEVER give to children under 16 — risk of Reye's syndrome (rare but fatal brain/liver condition). "
        "Stop 7 days before surgery. Avoid with active stomach ulcers."
    ),
    "diclofenac": (
        "💊 DICLOFENAC\n"
        "Brands: Voltaren, Voltarol, Cataflam\n\n"
        "Class: NSAID\n"
        "Uses: Arthritis, acute pain, period pain, back pain, gout, post-surgical pain. Also available as topical gel.\n\n"
        "Dosage:\n"
        "• Oral: 25–50mg 2–3 times daily with food. Max 150mg/day.\n"
        "• Topical gel: Apply 2–4g to affected area 3–4 times daily.\n\n"
        "Side effects: GI upset, fluid retention, elevated blood pressure, liver enzyme elevation.\n\n"
        "⚠️ Higher cardiovascular risk than other NSAIDs. Avoid in heart disease, kidney disease, and elderly. "
        "Gel form has fewer systemic side effects."
    ),
    "codeine": (
        "💊 CODEINE\n"
        "Brands: Tylenol with Codeine, Solpadeine, Nurofen Plus (with ibuprofen)\n\n"
        "Class: Opioid analgesic (weak)\n"
        "Uses: Moderate pain not relieved by paracetamol/ibuprofen alone. Also used as cough suppressant.\n\n"
        "Dosage:\n"
        "• Adults: 15–60mg every 4–6 hours. Max 240mg/day.\n"
        "• Not recommended for children under 12.\n\n"
        "Onset: 30–60 min. Duration: 4–6 hours.\n\n"
        "Side effects: Constipation, drowsiness, nausea, dizziness, dependence with prolonged use.\n\n"
        "⚠️ Controlled substance in many countries. Risk of addiction. "
        "Some people are 'ultra-rapid metabolisers' — codeine converts to morphine too fast, causing dangerous respiratory depression. "
        "Never use with alcohol. Do NOT use in children, breastfeeding mothers, or those with breathing problems."
    ),
    "tramadol": (
        "💊 TRAMADOL\n"
        "Brands: Ultram, Tramal, Zydol\n\n"
        "Class: Opioid analgesic (moderate)\n"
        "Uses: Moderate to severe pain.\n\n"
        "Dosage:\n"
        "• Adults: 50–100mg every 4–6 hours. Max 400mg/day.\n"
        "• Elderly: Max 300mg/day.\n\n"
        "Side effects: Nausea, dizziness, constipation, headache, sweating, seizures (at high doses), serotonin syndrome.\n\n"
        "Interactions: SSRIs, MAOIs, other opioids, alcohol, benzodiazepines — risk of serotonin syndrome or CNS depression.\n\n"
        "⚠️ Controlled substance. High addiction potential. Never combine with alcohol or sedatives. "
        "Can lower seizure threshold. Not for patients with epilepsy. Requires prescription."
    ),
    "morphine": (
        "💊 MORPHINE\n"
        "Brands: MST Continus, Oramorph, Zomorph\n\n"
        "Class: Strong opioid analgesic\n"
        "Uses: Severe pain — cancer pain, post-surgical pain, end-of-life care, acute MI chest pain.\n\n"
        "Dosage: Strictly titrated by doctor. Typical starting oral dose: 5–10mg every 4 hours.\n\n"
        "Side effects: Constipation (always co-prescribe laxative), nausea, sedation, respiratory depression, dependence.\n\n"
        "⚠️ Prescription only. Respiratory depression risk — antidote is Naloxone. "
        "Never use without medical supervision. Overdose can be fatal."
    ),

    # ── ANTIBIOTICS ───────────────────────────────────────────────────────────
    "antibiotic": (
        "💊 ANTIBIOTICS — General Guide\n\n"
        "Antibiotics treat BACTERIAL infections only — they do NOT work on viruses (colds, flu, COVID-19).\n\n"
        "Common classes and uses:\n\n"
        "🔹 Penicillins:\n"
        "• Amoxicillin — throat, ear, chest, urinary infections. 250–500mg 3x/day.\n"
        "• Co-amoxiclav (Augmentin) — broader spectrum, skin/bite wounds. 375–625mg 3x/day.\n\n"
        "🔹 Macrolides (for penicillin allergy):\n"
        "• Azithromycin (Z-pack) — chest, STIs, atypical pneumonia. 500mg day 1, then 250mg days 2–5.\n"
        "• Clarithromycin — chest, H. pylori. 250–500mg 2x/day.\n\n"
        "🔹 Fluoroquinolones:\n"
        "• Ciprofloxacin — UTIs, gut infections, anthrax. 250–500mg 2x/day.\n"
        "• Levofloxacin — community-acquired pneumonia, UTIs. 500mg once daily.\n\n"
        "🔹 Tetracyclines:\n"
        "• Doxycycline — acne, STIs, Lyme disease, malaria prevention. 100mg 2x/day.\n\n"
        "🔹 Nitroimidazoles:\n"
        "• Metronidazole — dental, gut (C. diff, Giardia), anaerobic infections. 400mg 3x/day.\n\n"
        "🔹 Cephalosporins:\n"
        "• Cefalexin — skin, UTI, respiratory. 250–500mg 4x/day.\n"
        "• Ceftriaxone (IV) — serious infections, meningitis, sepsis.\n\n"
        "🔹 Glycopeptides:\n"
        "• Vancomycin (IV) — MRSA, serious Gram-positive infections.\n\n"
        "⚠️ CRITICAL RULES:\n"
        "1. Always complete the full course — stopping early causes resistance.\n"
        "2. Never share antibiotics or take leftover ones.\n"
        "3. Antibiotic resistance is a global emergency — only use when prescribed.\n"
        "4. Common side effects: diarrhoea, nausea, yeast infections. Take probiotics during course."
    ),
    "amoxicillin": (
        "💊 AMOXICILLIN\n"
        "Brands: Amoxil, Trimox, Moxatag\n\n"
        "Class: Penicillin antibiotic\n"
        "Uses: Throat infections (strep), ear infections, chest infections, UTIs, dental abscess, Lyme disease, H. pylori (with others).\n\n"
        "Dosage:\n"
        "• Adults: 250–500mg every 8 hours, or 500–875mg every 12 hours. 5–10 day course.\n"
        "• Children: 25–45mg/kg/day divided every 8–12 hours.\n"
        "• Severe infections: 875mg–1g every 8 hours.\n\n"
        "Side effects: Diarrhoea, nausea, rash, yeast infection. Rare: severe allergic reaction (anaphylaxis).\n\n"
        "⚠️ Tell doctor if you have penicillin allergy. "
        "Complete the full course. Rash doesn't always mean allergy — consult pharmacist."
    ),
    "azithromycin": (
        "💊 AZITHROMYCIN\n"
        "Brands: Zithromax, Azithrocin, Z-pack\n\n"
        "Class: Macrolide antibiotic\n"
        "Uses: Community-acquired pneumonia, sinusitis, bronchitis, STIs (Chlamydia, Gonorrhoea), skin infections, typhoid.\n\n"
        "Dosage:\n"
        "• Adults: 500mg on day 1, then 250mg on days 2–5 (Z-pack).\n"
        "• STI (Chlamydia): Single 1g dose.\n"
        "• Pneumonia: 500mg daily for 3 days.\n\n"
        "Side effects: Nausea, diarrhoea, abdominal pain, QT prolongation (heart rhythm).\n\n"
        "⚠️ Avoid in patients with heart arrhythmias or QT prolongation. "
        "Do not take with antacids — space 2 hours apart. Can interact with Warfarin."
    ),
    "metronidazole": (
        "💊 METRONIDAZOLE\n"
        "Brands: Flagyl, Metrogel, Metronide\n\n"
        "Class: Nitroimidazole antibiotic/antiprotozoal\n"
        "Uses: Anaerobic bacterial infections, dental infections, Bacterial Vaginosis, Trichomonas, Giardia, C. difficile, H. pylori, pelvic inflammatory disease.\n\n"
        "Dosage:\n"
        "• Dental/oral infections: 400mg 3x/day for 5–7 days.\n"
        "• BV/Trichomonas: 400–500mg 2x/day for 5–7 days, or single 2g dose.\n"
        "• C. diff: 500mg 3x/day for 10–14 days.\n\n"
        "Side effects: Metallic taste, nausea, headache, dark urine. Rare: peripheral neuropathy (long-term use).\n\n"
        "⚠️ ABSOLUTELY NO ALCOHOL during treatment and 48 hours after — causes severe nausea/vomiting (disulfiram-like reaction). "
        "Avoid in first trimester pregnancy."
    ),
    "ciprofloxacin": (
        "💊 CIPROFLOXACIN\n"
        "Brands: Cipro, Ciproxin, Ciloxan\n\n"
        "Class: Fluoroquinolone antibiotic\n"
        "Uses: UTIs, prostatitis, gastroenteritis, typhoid, anthrax, some respiratory infections, bone/joint infections.\n\n"
        "Dosage:\n"
        "• UTI (uncomplicated): 250mg 2x/day for 3 days.\n"
        "• UTI (complicated)/prostatitis: 500mg 2x/day for 7–14 days.\n"
        "• Gastroenteritis: 500mg 2x/day for 5–7 days.\n\n"
        "Side effects: Nausea, diarrhoea, headache, dizziness, tendon damage (especially Achilles), photosensitivity.\n\n"
        "Interactions: Antacids (separate by 2+ hours), Warfarin, NSAIDs, dairy products reduce absorption.\n\n"
        "⚠️ Risk of tendon rupture — especially in elderly and those on steroids. "
        "Avoid in children and pregnancy. Avoid direct sunlight. Take on empty stomach or with light meal."
    ),
    "doxycycline": (
        "💊 DOXYCYCLINE\n"
        "Brands: Vibramycin, Doryx, Oracea\n\n"
        "Class: Tetracycline antibiotic\n"
        "Uses: Acne, Chlamydia, Lyme disease, malaria prevention, community-acquired pneumonia, rosacea, Rocky Mountain spotted fever.\n\n"
        "Dosage:\n"
        "• Standard: 100mg 2x/day (loading dose 200mg on day 1).\n"
        "• Acne: 100mg once daily for 3–6 months.\n"
        "• Malaria prevention: 100mg daily, starting 1–2 days before travel.\n\n"
        "Side effects: Photosensitivity, nausea, oesophageal irritation, yeast infection.\n\n"
        "⚠️ Take with full glass of water and remain upright for 30 min — prevents oesophageal ulcers. "
        "Avoid dairy, antacids, iron within 2 hours. Use sunscreen daily. "
        "NOT for children under 8 or pregnant/breastfeeding women."
    ),

    # ── CARDIOVASCULAR ────────────────────────────────────────────────────────
    "blood pressure": (
        "💊 BLOOD PRESSURE MEDICATIONS\n\n"
        "Normal BP: Below 120/80 mmHg\n"
        "Hypertension: 130/80 mmHg or above\n\n"
        "Classes of antihypertensives:\n\n"
        "🔹 ACE Inhibitors (first-line):\n"
        "• Ramipril, Lisinopril, Enalapril, Perindopril\n"
        "• Uses: Hypertension, heart failure, diabetic kidney protection.\n"
        "• Side effects: Dry cough (10–15%), hyperkalaemia, angioedema (rare but serious).\n\n"
        "🔹 ARBs (for ACE inhibitor cough):\n"
        "• Losartan, Valsartan, Candesartan, Irbesartan\n"
        "• Similar to ACE inhibitors but less cough. Avoid in pregnancy.\n\n"
        "🔹 Calcium Channel Blockers:\n"
        "• Amlodipine, Nifedipine, Diltiazem, Verapamil\n"
        "• Side effects: Ankle swelling, flushing, constipation (Verapamil).\n\n"
        "🔹 Thiazide Diuretics:\n"
        "• Bendroflumethiazide, Indapamide, Hydrochlorothiazide\n"
        "• Side effects: Hyponatraemia, hypokalaemia, gout, elevated glucose.\n\n"
        "🔹 Beta-Blockers:\n"
        "• Atenolol, Bisoprolol, Metoprolol, Propranolol, Carvedilol\n"
        "• Uses: Hypertension, angina, heart failure, arrhythmias, anxiety.\n"
        "• Side effects: Fatigue, cold extremities, bradycardia, impotence. Do not stop abruptly.\n\n"
        "🔹 Alpha-Blockers:\n"
        "• Doxazosin — also used for BPH (enlarged prostate).\n\n"
        "Lifestyle:\n"
        "• DASH diet (low salt, high potassium), regular exercise, weight loss, limit alcohol, stop smoking.\n\n"
        "⚠️ Never stop BP medications without doctor advice — rebound hypertension can be dangerous."
    ),
    "cholesterol": (
        "💊 CHOLESTEROL MEDICATIONS\n\n"
        "High LDL cholesterol increases risk of heart attack and stroke.\n\n"
        "Target levels:\n"
        "• Total cholesterol: Below 5 mmol/L\n"
        "• LDL: Below 3 mmol/L (below 1.8 in high-risk patients)\n"
        "• HDL: Above 1.0 (men), 1.2 (women)\n"
        "• Triglycerides: Below 1.7 mmol/L\n\n"
        "Medications:\n\n"
        "🔹 Statins (first-line):\n"
        "• Atorvastatin (most potent), Rosuvastatin, Simvastatin, Pravastatin.\n"
        "• Dose: Atorvastatin 10–80mg once daily at night.\n"
        "• Side effects: Muscle aches (myopathy), liver enzyme elevation, rarely rhabdomyolysis.\n\n"
        "🔹 Ezetimibe — reduces cholesterol absorption. Often combined with statins. 10mg daily.\n\n"
        "🔹 PCSK9 Inhibitors — injectable, highly effective. Evolocumab, Alirocumab. For high-risk patients.\n\n"
        "🔹 Fibrates — primarily lower triglycerides. Fenofibrate, Gemfibrozil.\n\n"
        "🔹 Omega-3 fatty acids (Prescription strength) — reduce triglycerides.\n\n"
        "Lifestyle:\n"
        "• Reduce saturated fats, trans fats. Increase fibre, oily fish, nuts.\n"
        "• Exercise 150 min/week. Lose excess weight. Stop smoking.\n\n"
        "⚠️ Report muscle pain or weakness immediately when taking statins — may indicate myopathy."
    ),
    "heart attack": (
        "🚨 HEART ATTACK (Myocardial Infarction) — Emergency Information\n\n"
        "Warning signs: Chest pain/pressure/tightness (may radiate to arm, jaw, back), shortness of breath, "
        "sweating, nausea, dizziness, sudden fatigue.\n\n"
        "IMMEDIATE ACTION:\n"
        "1. Call emergency services (999/911/112) IMMEDIATELY.\n"
        "2. Chew 300mg Aspirin (if not allergic and not already on it).\n"
        "3. Rest in a comfortable position (usually sitting up).\n"
        "4. Loosen tight clothing.\n"
        "5. If unconscious and not breathing — start CPR.\n\n"
        "Medications used in treatment:\n"
        "• Thrombolytics (clot busters): Alteplase, Tenecteplase — given in hospital.\n"
        "• Antiplatelet: Aspirin + Clopidogrel/Ticagrelor (dual antiplatelet therapy).\n"
        "• Anticoagulants: Heparin, Enoxaparin.\n"
        "• Beta-blockers, ACE inhibitors, Nitrates, Statins — started after stabilisation.\n\n"
        "⚠️ Every minute counts in a heart attack — 'Time is muscle'. Call emergency services immediately."
    ),
    "warfarin": (
        "💊 WARFARIN\n"
        "Brands: Coumadin, Marevan\n\n"
        "Class: Anticoagulant (blood thinner)\n"
        "Uses: Atrial fibrillation (stroke prevention), DVT/PE treatment and prevention, mechanical heart valves.\n\n"
        "Dosage: Highly individualised — based on INR (target usually 2–3, mechanical valves 2.5–3.5).\n"
        "Requires regular INR blood monitoring.\n\n"
        "Interactions (EXTENSIVE):\n"
        "• Increases effect: Aspirin, NSAIDs, Amiodarone, Fluconazole, Metronidazole, Ciprofloxacin, Clarithromycin, Omeprazole.\n"
        "• Decreases effect: Rifampicin, Carbamazepine, St John's Wort, Vitamin K-rich foods.\n\n"
        "Food interactions: Consistent Vitamin K intake is crucial — avoid sudden large changes in green vegetables (spinach, kale, broccoli).\n\n"
        "Side effects: Bleeding (minor to major), bruising, rare skin necrosis.\n\n"
        "⚠️ Signs of dangerous bleeding: Blood in urine (pink/red), black stools, coughing blood, severe headache. "
        "Seek emergency care immediately. Antidote: Vitamin K (Phytomenadione), Prothrombin complex concentrate."
    ),

    # ── DIABETES ──────────────────────────────────────────────────────────────
    "diabetes": (
        "💊 DIABETES MEDICATIONS & MANAGEMENT\n\n"
        "Type 1: Autoimmune — beta cells destroyed, requires insulin.\n"
        "Type 2: Insulin resistance — managed with lifestyle + oral medications ± insulin.\n\n"
        "Normal glucose: Fasting <5.6 mmol/L, 2hr post-meal <7.8 mmol/L, HbA1c <48 mmol/mol (6.5%).\n\n"
        "🔹 Biguanides (first-line T2DM):\n"
        "• Metformin 500–2000mg daily with meals. Reduces glucose production.\n"
        "• Side effects: GI upset, rarely lactic acidosis. Take with food to reduce GI side effects.\n\n"
        "🔹 SGLT2 Inhibitors (heart & kidney protective):\n"
        "• Empagliflozin, Dapagliflozin, Canagliflozin.\n"
        "• Also reduce heart failure hospitalisations and kidney disease progression.\n"
        "• Side effects: Genital thrush, UTIs, DKA (rare).\n\n"
        "🔹 GLP-1 Receptor Agonists (also aid weight loss):\n"
        "• Liraglutide (Victoza), Semaglutide (Ozempic/Wegovy), Dulaglutide.\n"
        "• Injectable (once weekly or daily). Significant cardiovascular benefit.\n"
        "• Side effects: Nausea, vomiting, pancreatitis (rare).\n\n"
        "🔹 DPP-4 Inhibitors (Gliptins):\n"
        "• Sitagliptin, Saxagliptin, Linagliptin. Well tolerated, weight neutral.\n\n"
        "🔹 Sulphonylureas:\n"
        "• Gliclazide, Glibenclamide, Glimepiride. Stimulate insulin release.\n"
        "• Side effects: Hypoglycaemia, weight gain.\n\n"
        "🔹 Insulin types:\n"
        "• Rapid-acting: Novorapid, Humalog, Apidra — given with meals.\n"
        "• Short-acting: Actrapid, Humulin R — 30 min before meals.\n"
        "• Intermediate: Humulin N, Insulatard — once/twice daily.\n"
        "• Long-acting: Lantus (Glargine), Levemir (Detemir), Tresiba (Degludec) — once daily basal.\n\n"
        "Hypoglycaemia (low blood sugar <4 mmol/L):\n"
        "• Symptoms: Shaking, sweating, confusion, palpitations.\n"
        "• Treatment: 15–20g fast-acting carbs (glucose tablets, fruit juice, regular cola). Re-check in 15 min.\n\n"
        "⚠️ Never skip meals on insulin or sulphonylureas — risk of dangerous hypoglycaemia."
    ),
    "metformin": (
        "💊 METFORMIN\n"
        "Brands: Glucophage, Glumetza, Fortamet\n\n"
        "Class: Biguanide antidiabetic\n"
        "Uses: Type 2 diabetes (first-line), PCOS, prediabetes, weight management.\n\n"
        "Dosage:\n"
        "• Start: 500mg once or twice daily with meals.\n"
        "• Increase gradually to 1000–2000mg/day over weeks to minimise GI effects.\n"
        "• Max: 3000mg/day.\n\n"
        "Mechanism: Reduces hepatic glucose production, increases insulin sensitivity.\n\n"
        "Side effects: Diarrhoea, nausea, abdominal discomfort (usually temporary), B12 deficiency (long-term).\n\n"
        "Interactions: Alcohol (lactic acidosis risk), contrast dye (stop 48h before imaging), iodine contrast.\n\n"
        "⚠️ Stop before surgery or contrast procedures. Check eGFR — contraindicated if eGFR <30. "
        "Monitor B12 levels annually. Does NOT cause hypoglycaemia alone."
    ),
    "insulin": (
        "💊 INSULIN — Complete Guide\n\n"
        "Insulin is a hormone that controls blood glucose. Essential for Type 1 diabetes, often needed in Type 2.\n\n"
        "Types and duration:\n"
        "• Rapid-acting (Novorapid, Humalog, Apidra): Onset 10–20 min, peak 1–3h, duration 3–5h. Give with meals.\n"
        "• Short-acting (Actrapid, Humulin R): Onset 30 min, peak 2–4h, duration 5–8h. Give 30 min before meal.\n"
        "• Intermediate (NPH — Humulin N, Insulatard): Onset 1–4h, peak 4–10h, duration 10–16h.\n"
        "• Long-acting (Glargine/Lantus, Detemir/Levemir): Onset 1–4h, no peak, duration 20–24h. Once daily basal.\n"
        "• Ultra-long (Degludec/Tresiba): Duration 42+ hours. Very stable.\n"
        "• Premixed (e.g. Novomix 30, Humulin 70/30): Combination of rapid and intermediate.\n\n"
        "Storage:\n"
        "• Unopened: Refrigerate 2–8°C.\n"
        "• In use: Room temperature up to 28 days (some up to 42 days — check label).\n"
        "• Never freeze. Discard if cloudy (except NPH which should be cloudy).\n\n"
        "Injection sites: Abdomen (fastest), thigh, buttock, upper arm. Rotate sites.\n\n"
        "Hypoglycaemia treatment: 15g fast-acting carbs. If unconscious: Glucagon injection or IV dextrose.\n\n"
        "⚠️ Insulin errors can be fatal. Always double-check dose, type, and units. "
        "Never share pens or needles. Store correctly."
    ),

    # ── RESPIRATORY ───────────────────────────────────────────────────────────
    "asthma": (
        "💊 ASTHMA MEDICATIONS\n\n"
        "Asthma causes airway inflammation, narrowing, and excess mucus.\n"
        "Symptoms: Wheeze, cough (especially night/morning), shortness of breath, chest tightness.\n\n"
        "🔹 Relievers (SABA — Short-Acting Beta-2 Agonists):\n"
        "• Salbutamol (Ventolin — blue inhaler), Terbutaline.\n"
        "• Use for immediate relief. Onset 5–15 min. Duration 4–6 hours.\n"
        "• Technique: Shake, exhale, inhale slowly, hold 10 sec.\n\n"
        "🔹 Preventers (ICS — Inhaled Corticosteroids):\n"
        "• Beclometasone, Budesonide, Fluticasone (brown/orange/purple inhalers).\n"
        "• Must be used DAILY even when well — reduces inflammation over time.\n"
        "• Rinse mouth after use to prevent oral thrush.\n\n"
        "🔹 Long-acting relievers (LABA):\n"
        "• Salmeterol, Formoterol — always combined with ICS (never alone in asthma).\n\n"
        "🔹 Combination inhalers:\n"
        "• Seretide (Fluticasone + Salmeterol), Symbicort (Budesonide + Formoterol), Fostair.\n\n"
        "🔹 Oral:\n"
        "• Montelukast (leukotriene antagonist) — add-on therapy, also useful in allergic rhinitis.\n"
        "• Prednisolone (oral steroid) — for acute exacerbations.\n"
        "• Theophylline — bronchodilator, requires blood level monitoring.\n\n"
        "Asthma attack management:\n"
        "1. Sit upright, stay calm.\n"
        "2. Use reliever inhaler (Salbutamol) — 4–10 puffs, 1 per minute.\n"
        "3. If no improvement in 15 min — call emergency services.\n\n"
        "⚠️ If you use reliever >3x/week, your asthma is not well controlled — see your doctor."
    ),
    "copd": (
        "💊 COPD — Chronic Obstructive Pulmonary Disease\n\n"
        "COPD is a progressive lung disease causing airflow obstruction — includes chronic bronchitis and emphysema.\n"
        "Main cause: Smoking (90% of cases).\n\n"
        "Symptoms: Persistent cough, increased mucus, breathlessness on exertion, wheeze.\n\n"
        "Medications:\n"
        "🔹 SABA (Short-acting bronchodilators): Salbutamol, Ipratropium — for immediate symptom relief.\n"
        "🔹 LAMA (Long-acting antimuscarinics — first-line maintenance):\n"
        "• Tiotropium (Spiriva), Umeclidinium, Glycopyrronium — once daily.\n"
        "🔹 LABA: Salmeterol, Formoterol, Indacaterol.\n"
        "🔹 LAMA+LABA combinations: Anoro, Spiolto, Ultibro.\n"
        "🔹 ICS — added in frequent exacerbators.\n"
        "🔹 Triple therapy (ICS+LAMA+LABA): Trelegy, Trimbow.\n"
        "🔹 Roflumilast (PDE4 inhibitor) — reduces exacerbations in severe COPD.\n\n"
        "Other management:\n"
        "• Pulmonary rehabilitation — most effective non-drug intervention.\n"
        "• Stop smoking — most important intervention.\n"
        "• Annual flu vaccine + pneumococcal vaccine.\n"
        "• Oxygen therapy if pO2 <7.3 kPa.\n\n"
        "⚠️ COPD is not reversible, but progression can be slowed. Stopping smoking is the single most effective intervention."
    ),

    # ── GI ────────────────────────────────────────────────────────────────────
    "omeprazole": (
        "💊 OMEPRAZOLE\n"
        "Brands: Losec, Prilosec, Zegerid\n\n"
        "Class: Proton Pump Inhibitor (PPI)\n"
        "Uses: GERD/acid reflux, peptic ulcers, H. pylori eradication (with antibiotics), NSAID-induced ulcer prevention, Zollinger-Ellison syndrome.\n\n"
        "Dosage:\n"
        "• GERD: 20mg once daily before breakfast for 4–8 weeks.\n"
        "• Ulcer healing: 20–40mg once daily for 4–8 weeks.\n"
        "• H. pylori: 20mg 2x/day + 2 antibiotics for 7–14 days.\n\n"
        "Onset: Full effect in 1–4 days.\n\n"
        "Long-term risks: Magnesium deficiency, B12 deficiency, increased fracture risk, increased C. diff risk, hyponatraemia.\n\n"
        "Interactions: Clopidogrel (reduces antiplatelet effect), Methotrexate, Warfarin.\n\n"
        "⚠️ Do not take long-term without medical review. Take 30–60 min before breakfast. "
        "Other PPIs: Lansoprazole, Pantoprazole, Esomeprazole — similar class."
    ),
    "antihistamine": (
        "💊 ANTIHISTAMINES\n\n"
        "Class: H1-receptor antagonists\n"
        "Uses: Allergies, hay fever, urticaria (hives), allergic rhinitis, insect bites, motion sickness.\n\n"
        "🔹 First-generation (sedating):\n"
        "• Chlorphenamine (Piriton): 4mg every 4–6 hours. Causes drowsiness — useful at night.\n"
        "• Promethazine (Phenergan): 10–25mg. Also used for motion sickness and sleep.\n"
        "• Diphenhydramine (Benadryl): 25–50mg. Also used as sleep aid.\n\n"
        "🔹 Second-generation (non-sedating, preferred):\n"
        "• Loratadine (Claritin): 10mg once daily.\n"
        "• Cetirizine (Zyrtec): 10mg once daily.\n"
        "• Fexofenadine (Allegra): 120–180mg once daily.\n"
        "• Bilastine: 20mg once daily (most non-sedating).\n\n"
        "Interactions: Alcohol, CNS depressants (enhance sedation with first-gen).\n\n"
        "⚠️ First-generation antihistamines impair driving and operating machinery. "
        "Not recommended in elderly — risk of urinary retention, confusion, falls. "
        "For severe anaphylaxis, use Adrenaline (Epinephrine) first — antihistamines alone are NOT sufficient."
    ),
    "antacid": (
        "💊 ANTACIDS & ACID RELIEF\n\n"
        "Uses: Heartburn, indigestion, acid reflux, stomach upset.\n\n"
        "🔹 Simple antacids (neutralise acid — fast relief):\n"
        "• Calcium carbonate (Tums, Rennie): Chew 1–2 tablets as needed.\n"
        "• Magnesium hydroxide (Milk of Magnesia): 5–15ml as needed. Also laxative.\n"
        "• Aluminium hydroxide: Often combined with Mg (Maalox, Gaviscon).\n"
        "• Sodium bicarbonate: Fast but causes gas and rebound acidity.\n\n"
        "🔹 Alginate preparations:\n"
        "• Gaviscon — forms a raft on stomach contents, prevents reflux. Ideal for GERD.\n\n"
        "🔹 H2 antagonists (longer-acting than antacids):\n"
        "• Ranitidine (withdrawn due to NDMA concerns — use alternatives).\n"
        "• Famotidine (Pepcid): 20–40mg once or twice daily.\n"
        "• Cimetidine: 400mg twice daily (many drug interactions — largely replaced).\n\n"
        "🔹 PPIs (strongest acid suppression — see Omeprazole entry).\n\n"
        "Lifestyle: Small meals, avoid lying down after eating, reduce fatty/spicy foods, alcohol, caffeine, and smoking.\n\n"
        "⚠️ Antacids reduce absorption of many drugs — space 2 hours apart from other medications."
    ),
    "laxative": (
        "💊 LAXATIVES\n\n"
        "Types and uses:\n\n"
        "🔹 Bulk-forming (first-line for constipation):\n"
        "• Ispaghula husk (Fybogel), Methylcellulose, Psyllium.\n"
        "• Take with plenty of water. Effect in 12–72 hours. Safe long-term.\n\n"
        "🔹 Osmotic laxatives:\n"
        "• Macrogol (Movicol, Laxido) — draws water into bowel. Effect 24–48 hours. Very safe, first-line.\n"
        "• Lactulose — softens stool over 48–72 hours. Also used in hepatic encephalopathy.\n"
        "• Magnesium hydroxide — faster effect 6–12 hours.\n\n"
        "🔹 Stimulant laxatives (short-term use only):\n"
        "• Senna: 7.5–15mg at night. Effect 6–12 hours.\n"
        "• Bisacodyl: 5–10mg oral or suppository. Effect 6–12h oral, 15–60 min rectal.\n"
        "• Prolonged use causes dependency and electrolyte imbalance.\n\n"
        "🔹 Stool softeners:\n"
        "• Docusate sodium — especially useful post-surgery or in opioid-induced constipation.\n\n"
        "🔹 Rectal preparations:\n"
        "• Glycerol suppositories — very fast (15–30 min). Good for acute relief.\n\n"
        "⚠️ Address underlying cause of constipation first (diet, hydration, exercise, medication review). "
        "Stimulant laxatives should not be used long-term without medical advice."
    ),
    "antidiarrheal": (
        "💊 ANTIDIARRHOEALS\n\n"
        "🔹 Loperamide (Imodium):\n"
        "• Dose: 4mg initially, then 2mg after each loose stool. Max 16mg/day.\n"
        "• Works by slowing gut motility. Onset 1 hour.\n"
        "• Do NOT use in: Bloody diarrhoea, high fever, children under 12 — could worsen C. diff or bacterial infections.\n\n"
        "🔹 Oral Rehydration Salts (ORS — most important):\n"
        "• Dioralyte, Electrolade — replaces lost fluids and electrolytes.\n"
        "• Essential especially in children, elderly, or if vomiting/diarrhoea is severe.\n\n"
        "🔹 Bismuth subsalicylate (Pepto-Bismol):\n"
        "• Also has antibacterial properties. Useful for traveller's diarrhoea.\n"
        "• Side effect: Black stools and tongue (harmless).\n\n"
        "🔹 Probiotics — may reduce duration of infectious diarrhoea.\n\n"
        "⚠️ Most acute diarrhoea resolves in 2–3 days with hydration alone. "
        "Seek medical advice if: blood in stool, fever >38.5°C, signs of dehydration, or symptoms >7 days."
    ),

    # ── INFECTIONS & ANTIFUNGALS ──────────────────────────────────────────────
    "fluconazole": (
        "💊 FLUCONAZOLE\n"
        "Brands: Diflucan, Canesten Oral\n\n"
        "Class: Triazole antifungal\n"
        "Uses: Vaginal thrush (Candida), oral thrush, systemic Candida infections, Cryptococcal meningitis, ringworm.\n\n"
        "Dosage:\n"
        "• Vaginal thrush: Single 150mg oral dose.\n"
        "• Oral thrush: 50mg once daily for 7–14 days.\n"
        "• Systemic infections: 200–400mg daily — hospitalised patients.\n\n"
        "Interactions: MAJOR — Warfarin (increases bleeding), Statins (myopathy risk), Phenytoin, Carbamazepine, Ciclosporin, QT-prolonging drugs.\n\n"
        "Side effects: Nausea, headache, abdominal pain, elevated liver enzymes.\n\n"
        "⚠️ Significant drug interactions — always check with pharmacist. Avoid in liver disease. "
        "Topical antifungals (Clotrimazole cream) are preferred for skin infections to minimise interactions."
    ),
    "antiviral": (
        "💊 ANTIVIRALS\n\n"
        "🔹 Aciclovir (Zovirax):\n"
        "• Uses: Herpes simplex (cold sores, genital herpes), Herpes zoster (shingles), Chickenpox.\n"
        "• Cold sores (topical): Apply 5x/day for 5 days, starting at first tingle.\n"
        "• Genital herpes: 200–400mg 5x/day for 5–10 days.\n"
        "• Shingles: 800mg 5x/day for 7 days — start within 72 hours of rash.\n\n"
        "🔹 Oseltamivir (Tamiflu):\n"
        "• Uses: Influenza A and B — reduces duration by ~1.5 days if started within 48 hours.\n"
        "• Dose: 75mg 2x/day for 5 days.\n\n"
        "🔹 Antiretrovirals (HIV):\n"
        "• Highly individualised — always managed by specialist.\n"
        "• Common classes: NRTIs, NNRTIs, Protease inhibitors, Integrase inhibitors.\n\n"
        "🔹 COVID-19 antivirals:\n"
        "• Nirmatrelvir/Ritonavir (Paxlovid) — for high-risk patients within 5 days of symptoms.\n"
        "• Molnupiravir (Lagevrio) — alternative oral antiviral.\n\n"
        "⚠️ Antivirals are most effective when started early. Most common viruses (colds, flu) resolve without them."
    ),

    # ── ALLERGIES & ANAPHYLAXIS ───────────────────────────────────────────────
    "anaphylaxis": (
        "🚨 ANAPHYLAXIS — Severe Allergic Reaction — EMERGENCY\n\n"
        "Signs: Swelling of face/throat, difficulty breathing/swallowing, severe hives, "
        "drop in blood pressure, rapid/weak pulse, loss of consciousness, vomiting.\n\n"
        "IMMEDIATE ACTION:\n"
        "1. Call emergency services (999/911/112) IMMEDIATELY.\n"
        "2. Use Adrenaline (Epinephrine) auto-injector (EpiPen) — inject into outer thigh.\n"
        "   • EpiPen 0.3mg (adults), EpiPen Jr 0.15mg (children 15–30kg).\n"
        "3. Lay person flat with legs raised (if breathing OK). If breathing difficulty — sit up.\n"
        "4. A second EpiPen can be given after 5–15 min if no improvement.\n"
        "5. In hospital: IV/IM Adrenaline, IV Chlorphenamine, IV Hydrocortisone, IV fluids.\n\n"
        "Antihistamines and steroids are SECONDARY — adrenaline is always first.\n\n"
        "⚠️ Anyone who has experienced anaphylaxis should carry 2 EpiPens at all times. "
        "Referral to allergy specialist is essential. Wear a MedicAlert bracelet."
    ),

    # ── HORMONES ──────────────────────────────────────────────────────────────
    "contraception": (
        "💊 CONTRACEPTION — Pharmaceutical Options\n\n"
        "🔹 Combined Oral Contraceptive Pill (COCP):\n"
        "• Contains oestrogen + progestogen. 99%+ effective when taken correctly.\n"
        "• Examples: Microgynon, Yasmin, Cilest, Marvelon.\n"
        "• Take same time daily. Start first Sunday of period or day 1-5.\n"
        "• Side effects: Nausea, breast tenderness, mood changes, VTE risk (blood clots).\n\n"
        "🔹 Progestogen-only Pill (POP/Mini-pill):\n"
        "• Examples: Cerazette, Noriday, Norgeston.\n"
        "• Suitable for those who cannot take oestrogen (migraine with aura, smokers over 35, breastfeeding).\n"
        "• Must be taken within same 3-hour window daily (12 hours for desogestrel pills).\n\n"
        "🔹 Emergency contraception:\n"
        "• Levonorgestrel (Plan B, Levonelle): Within 72 hours (more effective the sooner taken).\n"
        "• Ulipristal acetate (EllaOne): Within 120 hours (5 days) — more effective later.\n"
        "• Copper IUD: Most effective emergency contraception, up to 5 days after unprotected sex.\n\n"
        "🔹 Long-acting reversible contraception (LARC):\n"
        "• Hormonal IUS (Mirena, Kyleena) — 3–8 years.\n"
        "• Copper IUD — 5–10 years, no hormones.\n"
        "• Implant (Nexplanon) — 3 years, arm implant.\n"
        "• Injectable (Depo-Provera) — every 12 weeks.\n\n"
        "⚠️ Antibiotics (except Rifampicin) do NOT reduce pill effectiveness — that was an old myth now disproven. "
        "However, vomiting within 2–3 hours of pill and diarrhoea does reduce effectiveness."
    ),
    "thyroid": (
        "💊 THYROID MEDICATIONS\n\n"
        "🔹 Hypothyroidism (underactive thyroid):\n"
        "• Levothyroxine (T4): Standard treatment. Start 25–50mcg daily, titrate based on TSH.\n"
        "• Take on empty stomach, 30–60 min before breakfast.\n"
        "• Separate from calcium, iron, antacids by 4 hours.\n"
        "• Annual TSH monitoring.\n"
        "• Signs of under-treatment: Fatigue, cold, weight gain, constipation, dry skin.\n"
        "• Signs of over-treatment: Palpitations, tremor, insomnia, weight loss, osteoporosis risk.\n\n"
        "🔹 Hyperthyroidism (overactive thyroid):\n"
        "• Carbimazole — blocks thyroid hormone production. 15–40mg daily initially.\n"
        "• Propylthiouracil (PTU) — alternative, especially in pregnancy.\n"
        "• Propranolol — for symptom control (tremor, palpitations) while awaiting drug effect.\n"
        "• Radioiodine (I-131) — definitive treatment.\n"
        "• Surgery (thyroidectomy) — for large goitres or cancer.\n\n"
        "⚠️ If on Carbimazole and develop sore throat or fever, stop immediately and get urgent blood count — risk of agranulocytosis."
    ),

    # ── GENERAL HEALTH ────────────────────────────────────────────────────────
    "headache": (
        "💊 HEADACHE — Types & Treatment\n\n"
        "Types:\n"
        "• Tension headache (most common) — band-like pressure, stress-related.\n"
        "• Migraine — throbbing, often one-sided, with nausea/light sensitivity, ± aura.\n"
        "• Cluster headache — severe, around one eye, in clusters.\n"
        "• Medication overuse headache — from taking pain relief >15 days/month.\n\n"
        "Tension headache treatment:\n"
        "• Paracetamol 1g, Ibuprofen 400mg, Aspirin 600mg.\n"
        "• Rest, hydration, stress reduction.\n\n"
        "Migraine treatment:\n"
        "• Mild: Paracetamol + Metoclopramide (for nausea), Ibuprofen.\n"
        "• Moderate-severe: Triptans — Sumatriptan 50–100mg oral, 6mg SC, or nasal spray.\n"
        "  Other triptans: Rizatriptan, Zolmitriptan, Naratriptan, Eletriptan.\n"
        "• Anti-emetics: Metoclopramide 10mg, Prochlorperazine.\n"
        "• Preventives (if >4/month): Propranolol, Topiramate, Amitriptyline, Candesartan, Botulinum toxin, CGRP antagonists (Erenumab, Fremanezumab).\n\n"
        "⚠️ Red flags — seek emergency care: Sudden worst headache of life (thunderclap), headache with fever+stiff neck (meningitis), "
        "headache with neurological symptoms, headache after head injury, progressive worsening headache."
    ),
    "fever": (
        "💊 FEVER — Management\n\n"
        "Fever = temperature >38°C (100.4°F). It's a sign your immune system is fighting infection.\n\n"
        "Management:\n"
        "• Paracetamol 500mg–1g every 4–6 hours (max 4g/day).\n"
        "• Ibuprofen 400mg every 6–8 hours with food (if not contraindicated).\n"
        "• Alternate paracetamol and ibuprofen every 3–4 hours if fever persists.\n"
        "• Stay well hydrated. Light clothing. Ventilated room.\n"
        "• Lukewarm sponging can help (not cold water or ice — causes shivering).\n\n"
        "Fever in children:\n"
        "• Paracetamol OR Ibuprofen (weight-based dosing).\n"
        "• Encourage fluids. Do not over-wrap.\n\n"
        "⚠️ Seek emergency care if: Fever >39.5°C not responding to medication, fever in infant under 3 months, "
        "fever with rash (especially non-blanching/purple), stiff neck, severe headache, confusion, difficulty breathing."
    ),
    "cold": (
        "💊 COMMON COLD — Treatment\n\n"
        "Caused by rhinovirus — antibiotics are useless.\n\n"
        "Symptom relief:\n"
        "• Paracetamol or Ibuprofen for fever/aches.\n"
        "• Decongestants: Pseudoephedrine (oral, max 7 days), Oxymetazoline/Xylometazoline (nasal sprays, max 7 days — rebound congestion risk).\n"
        "• Antihistamines: Chlorphenamine for runny nose and sneezing.\n"
        "• Saline nasal spray — safe, very effective for congestion.\n"
        "• Steam inhalation.\n"
        "• Warm honey-lemon drinks soothe sore throat.\n"
        "• Zinc lozenges (within 24h of onset) may reduce duration.\n"
        "• Vitamin C — modest benefit if taken regularly before illness.\n\n"
        "⚠️ Decongestant nasal sprays must NOT be used more than 7 days — cause rebound congestion (rhinitis medicamentosa). "
        "Avoid giving cold medicines to children under 6."
    ),
    "sleep": (
        "💊 SLEEP — Medications & Hygiene\n\n"
        "Sleep disorders: Insomnia (difficulty falling/staying asleep), sleep apnoea, restless legs syndrome.\n\n"
        "Sleep hygiene (try first):\n"
        "• Consistent sleep schedule, even on weekends.\n"
        "• Avoid screens 1 hour before bed (blue light blocks melatonin).\n"
        "• Dark, cool, quiet room (ideal 16–19°C).\n"
        "• Avoid caffeine after 2pm, alcohol within 3 hours of bed.\n"
        "• Exercise — but not within 3 hours of sleep.\n"
        "• Wind-down routine: reading, light stretching, bath.\n\n"
        "OTC sleep aids:\n"
        "• Melatonin: 0.5–5mg, 30–60 min before bed. Especially useful for jet lag. Very safe.\n"
        "• Diphenhydramine (Nytol, Sominex): 25–50mg. Sedating antihistamine. Short-term only.\n"
        "• Promethazine: 25mg — sedating antihistamine.\n\n"
        "Prescription:\n"
        "• Z-drugs: Zopiclone, Zolpidem — short-term only (2–4 weeks), risk of dependence.\n"
        "• Benzodiazepines: Temazepam, Nitrazepam — significant dependence risk, avoid long-term.\n"
        "• Low-dose Amitriptyline or Mirtazapine — for chronic insomnia (off-label).\n"
        "• Melatonin (Circadin 2mg) — prescription strength for those over 55.\n\n"
        "⚠️ Z-drugs and benzodiazepines should only be used short-term. CBT-I (Cognitive Behavioural Therapy for Insomnia) "
        "is the most effective long-term treatment for chronic insomnia."
    ),
    "not feeling good": (
        "💊 NOT FEELING WELL — General Self-Care\n\n"
        "Feeling unwell can have many causes — physical, emotional, or both.\n\n"
        "Physical check:\n"
        "• Take your temperature — fever above 38°C needs monitoring.\n"
        "• Check hydration — dark urine = dehydrated. Drink water.\n"
        "• Have you eaten? Low blood sugar causes fatigue, dizziness, irritability.\n"
        "• Any recent medication changes or missed doses?\n\n"
        "General self-care:\n"
        "• Rest — your body heals during sleep and rest.\n"
        "• Hydrate — water, clear broths, oral rehydration salts if needed.\n"
        "• Light, nutritious food — soups, fruits, porridge.\n"
        "• Fresh air and gentle movement if able.\n\n"
        "Emotional component:\n"
        "• Name what you're feeling — sometimes identifying the emotion brings relief.\n"
        "• Talk to someone you trust.\n"
        "• Be gentle with yourself — it's okay to not be okay.\n\n"
        "⚠️ Seek medical advice if symptoms last more than 3 days, are severe, or include high fever, chest pain, or breathing difficulty."
    ),
    "vitamins": (
        "💊 VITAMINS & SUPPLEMENTS — Key Information\n\n"
        "🔹 Vitamin D:\n"
        "• Deficiency is extremely common, especially in low-sunlight regions.\n"
        "• Dose: 400–1000 IU/day maintenance; 50,000 IU/week for deficiency (prescription).\n"
        "• Symptoms of deficiency: Fatigue, bone/muscle pain, low mood, frequent infections.\n\n"
        "🔹 Vitamin B12:\n"
        "• Essential for nerves and red blood cells. Deficiency causes anaemia and neuropathy.\n"
        "• At risk: Vegans/vegetarians, elderly, Metformin users, those with pernicious anaemia.\n"
        "• Oral: 1000mcg daily; IM injections every 3 months for pernicious anaemia.\n\n"
        "🔹 Folic Acid:\n"
        "• 400mcg daily for women trying to conceive and during first 12 weeks pregnancy.\n"
        "• 5mg daily if higher risk (previous neural tube defect, antiepileptic use, diabetes).\n\n"
        "🔹 Iron:\n"
        "• Ferrous sulphate 200mg 2–3x/day for iron-deficiency anaemia.\n"
        "• Take on empty stomach with Vitamin C for better absorption.\n"
        "• Side effects: Black stools, constipation, nausea.\n\n"
        "🔹 Magnesium:\n"
        "• 300–400mg/day. Helps sleep, muscle cramps, migraines, anxiety.\n"
        "• Magnesium glycinate is best tolerated. High doses cause diarrhoea.\n\n"
        "🔹 Zinc:\n"
        "• 8–11mg/day. Immune function, wound healing, taste/smell.\n"
        "• Excess zinc inhibits copper absorption.\n\n"
        "🔹 Omega-3 (Fish oil):\n"
        "• 1–4g/day EPA+DHA. Reduces triglycerides, anti-inflammatory, supports brain health.\n\n"
        "⚠️ Fat-soluble vitamins (A, D, E, K) accumulate in the body — toxicity is possible with excessive doses. "
        "Always inform your doctor of supplements taken — many interact with medications."
    ),
    "first aid": (
        "🩺 FIRST AID — Essential Guide\n\n"
        "🩹 Cuts/Wounds:\n"
        "• Clean with running water for 5–10 min. Apply antiseptic.\n"
        "• Apply firm pressure with clean cloth to stop bleeding.\n"
        "• Cover with sterile bandage. Deep/gaping wounds need stitches.\n\n"
        "🔥 Burns:\n"
        "• Cool under running cold water for 20 min (NOT ice, butter, or toothpaste).\n"
        "• Cover loosely with cling film or sterile dressing.\n"
        "• Seek care for: Burns larger than hand, facial/genital burns, full thickness burns, chemical/electrical burns.\n\n"
        "🫁 Choking:\n"
        "• Encourage coughing. If ineffective: 5 back blows, then 5 abdominal thrusts (Heimlich manoeuvre).\n"
        "• If unconscious — call 999, start CPR.\n\n"
        "🫀 CPR (Adults):\n"
        "• Call 999 first. 30 chest compressions (5–6cm deep, 100–120/min) + 2 rescue breaths.\n"
        "• Continue until help arrives or AED available.\n\n"
        "💊 Poisoning/Overdose:\n"
        "• Call 999 immediately. Do NOT induce vomiting.\n"
        "• Note substance taken and amount if possible.\n\n"
        "🤕 Fainting:\n"
        "• Lay person flat, raise legs. Loosen clothing. Ensure airway is open.\n\n"
        "🐍 Bites/Stings:\n"
        "• Snake bite: Immobilise limb, keep below heart level, go to hospital immediately.\n"
        "• Bee/wasp sting: Remove sting by scraping (not squeezing). Ice and antihistamine.\n"
        "• Anaphylaxis signs: Use EpiPen + call 999.\n\n"
        "⚠️ Always call emergency services (999/911/112) for life-threatening emergencies. "
        "Consider taking a certified first aid course."
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
        <audio id="az_{unique_id}" autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var a = document.getElementById("az_{unique_id}");
            if (a) a.play().catch(function(e) {{ console.log("Autoplay blocked:", e); }});
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
        speak("Sorry, I couldn't calculate that. Try: calculate 10 * 5")

def my_country():
    info = get_location_info()
    if info:
        speak(f"Based on your IP, you appear to be in {info['city']}, {info['country']}.")
    else:
        speak("Sorry, I could not detect your location right now.")

def world_situation():
    news = get_news()
    if news:
        speak(f"Here are today's top headlines:\n{news}")
    else:
        speak("The world situation is constantly evolving. Follow reliable sources like BBC, Reuters, or Al Jazeera.")

def weather_info():
    result, city = get_weather()
    if result:
        speak(f"Current weather in {city}: {result}.")
    else:
        speak("Sorry, I couldn't fetch the weather right now.")

def search_web(query: str):
    speak(f"Searching for: {query}")
    result = web_search(query)
    if result:
        speak(result)
    else:
        speak(f"I couldn't find a direct answer for '{query}'. Try Google, Wikipedia, or BBC.")

# ── Query handler ──────────────────────────────────────────────────────────────
def handle_query(user_input: str) -> bool:
    text = user_input.lower()

    if text == "exit":
        speak("Goodbye! Have a great day!"); return False
    elif any(w in text for w in ["hello", "hi", "hey"]):
        speak("Hello! How can I assist you today?")
    elif "how are you" in text:
        speak("I am doing well, thank you! How can I assist you today?")
    elif "your name" in text:
        speak("My name is Azile, your virtual assistant.")
    elif "who created you" in text or "creator" in text:
        speak("I was created by a talented developer using Python and AI technologies.")
    elif "what can you do" in text or "capabilities" in text:
        speak("I can answer questions, check time by location, weather, search the web, get news, tell jokes, do calculations, and give extensive health and medicine advice!")
    elif "help" in text:
        speak(HELP_TEXT)
    elif "time" in text:
        tell_time()
    elif "date" in text or "today" in text:
        tell_date()
    elif "weather" in text or "temperature" in text or "forecast" in text:
        weather_info()
    elif "news" in text or "headlines" in text or "world situation" in text or "current situation" in text:
        world_situation()
    elif text.startswith("search:") or text.startswith("search "):
        query = text.replace("search:", "").replace("search ", "", 1).strip()
        search_web(query)
    elif "joke" in text:
        tell_joke()
    elif text.startswith("calculate"):
        calculate(user_input)
    elif "country" in text or "location" in text or "where am i" in text or "city" in text:
        my_country()
    else:
        health_resp = get_health_response(text)
        if health_resp:
            speak(health_resp)
        elif any(w in text for w in ["sad", "lonely", "hopeless", "worthless", "crying", "cry", "suffering", "hurt", "suicid"]):
            speak(
                "I'm really sorry you're feeling this way. You are not alone, and it's okay to not be okay.\n\n"
                "Please consider:\n"
                "• Talking to someone you trust — a friend, family member, or counsellor.\n"
                "• Taking slow, deep breaths right now.\n"
                "• Being gentle with yourself.\n\n"
                "If things feel very dark, please reach out to a mental health crisis line in your country. "
                "You deserve support and care. 💙"
            )
        elif any(w in text for w in ["tired", "exhausted", "burnout", "burnt out", "overwhelmed", "cant cope", "can't cope"]):
            speak(
                "It sounds like you're running very low on energy. That's completely valid.\n\n"
                "Try to:\n"
                "• Take a short break — even 10 minutes outside helps.\n"
                "• Drink water and eat something nourishing.\n"
                "• Say no to one non-urgent thing today.\n"
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
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,
[data-testid="stMain"] p,[data-testid="stMain"] span,[data-testid="stMain"] label,
[data-testid="stMain"] li,.stMarkdown,.stMarkdown * {{ color: {fg} !important; }}
.chat-box {{
    background-color: {chat_bg} !important;
    border: 1px solid {chat_border} !important;
    border-radius: 10px; padding: 16px;
    height: 220px; overflow-y: auto; margin-bottom: 12px;
}}
.chat-box p, .chat-box strong {{ color: {fg} !important; }}
.stTextInput input {{
    background-color: {input_bg} !important;
    color: {fg} !important;
    border: 1px solid {input_bdr} !important;
    border-radius: 6px !important;
}}
.stTextInput label {{ color: {fg} !important; }}
.stButton > button, .stFormSubmitButton > button {{
    background-color: {btn_bg} !important;
    color: {fg} !important;
    border: 1px solid {btn_bdr} !important;
    border-radius: 6px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar tips ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Azile")
    st.markdown("**Virtual Assistant**")
    st.markdown("---")
    st.markdown("**💊 Medicine / Health:**")
    for t in ["paracetamol","ibuprofen","amoxicillin","metformin","omeprazole",
              "antihistamine","warfarin","diabetes","asthma","depression","anxiety","vitamins"]:
        st.markdown(f"- {t}")
    st.markdown("**🌐 General:**")
    for t in ["What time is it?","Weather","News","Search: topic","Calculate 25*4","What is my country?"]:
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
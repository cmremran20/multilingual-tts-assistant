"""
Multilingual AI Text-to-Speech Assistant
BIT4543 Artificial Intelligence - Group Project

How to run:
1. pip install -r requirements.txt
2. streamlit run app.py
"""

import asyncio
import os
from datetime import datetime

import streamlit as st
import edge_tts
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # makes langdetect results consistent

# Speech-to-text (microphone input) is optional — app still works without it
try:
    import speech_recognition as sr
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False


LANGUAGE_VOICES = {
    "en": {"name": "English", "flag": "🇺🇸", "voices": {
        "Female (US)": "en-US-JennyNeural",
        "Male (US)": "en-US-GuyNeural",
        "Female (UK)": "en-GB-SoniaNeural",
    }},
    "bn": {"name": "Bengali", "flag": "🇧🇩", "voices": {
        "Female (Bangladesh)": "bn-BD-NabanitaNeural",
        "Male (Bangladesh)": "bn-BD-PradeepNeural",
        "Female (India)": "bn-IN-TanishaaNeural",
        "Male (India)": "bn-IN-BashkarNeural",
    }},
    "ms": {"name": "Malay", "flag": "🇲🇾", "voices": {
        "Female (MY)": "ms-MY-YasminNeural",
        "Male (MY)": "ms-MY-OsmanNeural",
    }},
    "hi": {"name": "Hindi", "flag": "🇮🇳", "voices": {
        "Female (IN)": "hi-IN-SwaraNeural",
        "Male (IN)": "hi-IN-MadhurNeural",
    }},
    "zh-cn": {"name": "Mandarin", "flag": "🇨🇳", "voices": {
        "Female (CN)": "zh-CN-XiaoxiaoNeural",
        "Male (CN)": "zh-CN-YunxiNeural",
    }},
    "ar": {"name": "Arabic", "flag": "🇸🇦", "voices": {
        "Female (SA)": "ar-SA-ZariyahNeural",
        "Male (SA)": "ar-SA-HamedNeural",
    }},
    "ta": {"name": "Tamil", "flag": "🇮🇳", "voices": {
        "Female (IN)": "ta-IN-PallaviNeural",
        "Male (IN)": "ta-IN-ValluvarNeural",
    }},
}

OUTPUT_DIR = "generated_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def detect_language(text: str):
    try:
        code = detect(text)
        if code not in LANGUAGE_VOICES:
            base = code.split("-")[0]
            if base in LANGUAGE_VOICES:
                return base
            return "en"
        return code
    except Exception:
        return "en"



async def generate_speech(text: str, voice: str, rate: str, pitch: str, filename: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(filename)


def run_tts(text, voice, rate, pitch):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"speech_{timestamp}.mp3")
    asyncio.run(generate_speech(text, voice, rate, pitch, filename))
    return filename


def listen_from_microphone(duration=6):
    """Records from the default system microphone and returns recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
    try:
        # Uses Google's free Web Speech API (needs internet connection)
        text = recognizer.recognize_google(audio)
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand the audio. Please speak clearly and try again."
    except sr.RequestError:
        return None, "Speech recognition service unavailable (check your internet connection)."
    except Exception as e:
        return None, f"Microphone error: {e}"



st.set_page_config(
    page_title="Vocalis — Multilingual AI Speech Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
    --navy-950: #0A0F1E;
    --navy-900: #0F1830;
    --navy-800: #16213E;
    --navy-700: #1E2C4D;
    --teal: #2DE0C7;
    --teal-dim: #1B9E8C;
    --coral: #FF6B5B;
    --coral-dim: #E4523F;
    --text-hi: #EAF0FB;
    --text-lo: #8B97B8;
    --border: rgba(45, 224, 199, 0.14);
}

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse 900px 500px at 15% -10%, rgba(45,224,199,0.10), transparent 60%),
        radial-gradient(ellipse 700px 500px at 100% 0%, rgba(255,107,91,0.08), transparent 55%),
        var(--navy-950);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.4rem; max-width: 980px; }

/* ---------- Hero ---------- */
.vx-hero {
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 34px 38px 30px 38px;
    background: linear-gradient(160deg, rgba(30,44,77,0.65), rgba(15,24,48,0.55));
    position: relative;
    overflow: hidden;
    margin-bottom: 22px;
}
.vx-hero::after {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
    height: 1px; top: 0; opacity: 0.5;
}
.vx-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.12em;
    font-size: 12px;
    color: var(--teal);
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex; align-items: center; gap: 8px;
}
.vx-eyebrow .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--teal); box-shadow: 0 0 8px var(--teal);
}
.vx-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 40px;
    line-height: 1.08;
    color: var(--text-hi);
    margin: 0 0 10px 0;
}
.vx-title span { color: var(--teal); }
.vx-sub {
    color: var(--text-lo);
    font-size: 15.5px;
    max-width: 560px;
    line-height: 1.55;
    margin-bottom: 20px;
}

/* Waveform bars */
.vx-wave { display: flex; align-items: flex-end; gap: 4px; height: 34px; }
.vx-wave span {
    width: 4px; border-radius: 2px;
    background: linear-gradient(180deg, var(--teal), var(--teal-dim));
    animation: vxbar 1.15s ease-in-out infinite;
}
@keyframes vxbar {
    0%, 100% { transform: scaleY(0.35); opacity: 0.55; }
    50% { transform: scaleY(1); opacity: 1; }
}
.vx-wave span:nth-child(1){height:14px; animation-delay:0.0s}
.vx-wave span:nth-child(2){height:26px; animation-delay:0.1s}
.vx-wave span:nth-child(3){height:34px; animation-delay:0.2s}
.vx-wave span:nth-child(4){height:20px; animation-delay:0.3s}
.vx-wave span:nth-child(5){height:30px; animation-delay:0.4s}
.vx-wave span:nth-child(6){height:16px; animation-delay:0.5s}
.vx-wave span:nth-child(7){height:24px; animation-delay:0.6s}
.vx-wave span:nth-child(8){height:12px; animation-delay:0.7s}
.vx-wave span:nth-child(9){height:22px; animation-delay:0.8s}
.vx-wave span:nth-child(10){height:15px; animation-delay:0.9s}
.vx-wave span:nth-child(11){height:28px; animation-delay:1.0s}
.vx-wave span:nth-child(12){height:18px; animation-delay:1.1s}

/* ---------- Section labels ---------- */
.vx-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-lo);
    margin: 22px 0 8px 2px;
}

/* ---------- Streamlit widget restyling ---------- */
textarea,
.stTextArea textarea,
.stTextArea textarea:disabled,
.stTextArea > div,
.stTextArea > div > div,
.stTextArea [data-baseweb="textarea"],
.stTextArea [data-baseweb="base-input"] {
    background: #0F1830 !important;
    background-color: #0F1830 !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: #EAF0FB !important;
    font-size: 15px !important;
    -webkit-text-fill-color: #EAF0FB !important;
    caret-color: #EAF0FB !important;
}
.stTextArea textarea::placeholder {
    color: var(--text-lo) !important;
    opacity: 1 !important;
    -webkit-text-fill-color: var(--text-lo) !important;
}
.stTextArea textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 1px var(--teal) !important;
}
/* Force dark color-scheme everywhere so browsers don't auto-invert form fields */
html, body, .stApp, textarea, select, input, div[data-baseweb="select"], div[data-baseweb="popover"] {
    color-scheme: dark !important;
}

div[data-baseweb="select"] > div {
    background: #0F1830 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: var(--text-hi) !important;
}

/* ---------- Dropdown OPTIONS LIST (renders in a floating portal) ---------- */
div[data-baseweb="popover"] ul[role="listbox"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #0F1830 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
div[data-baseweb="popover"] li[role="option"],
li[role="option"] {
    background: #0F1830 !important;
    color: var(--text-hi) !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: rgba(45,224,199,0.15) !important;
    color: var(--teal) !important;
}
div[data-baseweb="popover"] * {
    color: var(--text-hi) !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--teal) !important;
    box-shadow: 0 0 10px rgba(45,224,199,0.6) !important;
}
.stSlider [data-baseweb="slider"] > div > div {
    background: var(--teal) !important;
}

/* Primary button = coral CTA */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--coral), var(--coral-dim)) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    border-radius: 11px !important;
    padding: 0.7rem 1.2rem !important;
    box-shadow: 0 6px 20px rgba(255,107,91,0.25);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 26px rgba(255,107,91,0.35);
}

.stDownloadButton > button {
    background: rgba(45,224,199,0.10) !important;
    border: 1px solid var(--teal) !important;
    color: var(--teal) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: rgba(45,224,199,0.18) !important;
}

/* Secondary buttons (mic button etc.) */
.stButton > button:not([kind="primary"]) {
    background: rgba(45,224,199,0.08) !important;
    border: 1px solid var(--border) !important;
    color: var(--teal) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(45,224,199,0.16) !important;
    border-color: var(--teal) !important;
}
.stButton > button:disabled {
    opacity: 0.35 !important;
}

.stAlert {
    background: rgba(45,224,199,0.08) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
}

audio { width: 100%; border-radius: 10px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy-900), var(--navy-950)) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-lo) !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: var(--text-hi) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Expander (history) */
.streamlit-expanderHeader {
    background: rgba(22,33,62,0.45) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

h3 { font-family: 'Space Grotesk', sans-serif !important; color: var(--text-hi) !important; }
p, label, span, div { color: var(--text-hi); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--text-lo) !important; }
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("### 🎙️ Vocalis")
    st.caption("Multilingual AI Speech Studio")
    st.markdown("---")
    st.markdown("**Project**")
    st.caption("BIT4543 — Artificial Intelligence\nGroup Project · Speech AI")
    st.markdown("---")
    st.markdown("**Engine**")
    st.caption("Microsoft Edge Neural TTS")
    st.markdown("**Detection**")
    st.caption("langdetect (statistical n-gram model)")
    st.markdown("---")
    st.markdown("**Supported Languages**")
    for code, meta in LANGUAGE_VOICES.items():
        st.caption(f"{meta['flag']}  {meta['name']}")


wave_bars = "".join(["<span></span>" for _ in range(12)])
st.markdown(f"""
<div class="vx-hero">
    <div class="vx-eyebrow"><span class="dot"></span> SPEECH AI · REAL-TIME SYNTHESIS</div>
    <div class="vx-title">Turn text into <span>natural speech</span><br>in any language.</div>
    <div class="vx-sub">Vocalis detects the language of your text automatically and synthesizes
    studio-quality neural speech — with adjustable voice, speed, and pitch — ready to play or download.</div>
    <div class="vx-wave">{wave_bars}</div>
</div>
""", unsafe_allow_html=True)


if "history" not in st.session_state:
    st.session_state.history = []
if "text_value" not in st.session_state:
    st.session_state.text_value = ""

st.markdown('<div class="vx-label">01 · INPUT TEXT</div>', unsafe_allow_html=True)

in_col, mic_col = st.columns([5, 1])
with mic_col:
    st.write("")  # small vertical alignment spacer
    mic_clicked = st.button("🎤 Speak", use_container_width=True,
                             disabled=not MIC_AVAILABLE,
                             help="Speak into your microphone instead of typing"
                                  if MIC_AVAILABLE else
                                  "Install SpeechRecognition + PyAudio to enable this (see README)")

if mic_clicked and MIC_AVAILABLE:
    with st.spinner("🎙️ Listening... speak now"):
        recognized_text, error = listen_from_microphone(duration=6)
    if recognized_text:
        st.session_state.text_value = recognized_text
        st.success(f"Heard: \"{recognized_text}\"")
    else:
        st.error(error)

with in_col:
    text_input = st.text_area(
        "Text",
        height=140,
        value=st.session_state.text_value,
        placeholder="Type or paste text, or click 🎤 Speak to talk instead — supports English, Bengali, Malay, Hindi, Mandarin, Arabic, Tamil...",
        label_visibility="collapsed",
        key="text_input_box",
    )
    st.session_state.text_value = text_input

if not MIC_AVAILABLE:
    st.caption("💡 Microphone input needs extra setup: `pip install SpeechRecognition pyaudio` (see README).")

detected_code = detect_language(text_input) if text_input.strip() else "en"

if text_input.strip():
    lang_meta = LANGUAGE_VOICES.get(detected_code, LANGUAGE_VOICES["en"])
    st.info(f"{lang_meta['flag']}  **Detected Language:** {lang_meta['name']}  ·  `{detected_code}`")

st.markdown('<div class="vx-label">02 · VOICE CONFIGURATION</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

lang_options = list(LANGUAGE_VOICES.keys())
default_index = lang_options.index(detected_code) if detected_code in lang_options else 0

with col1:
    selected_lang = st.selectbox(
        "Language",
        options=lang_options,
        format_func=lambda c: f"{LANGUAGE_VOICES[c]['flag']}  {LANGUAGE_VOICES[c]['name']}",
        index=default_index,
    )

with col2:
    voice_options = LANGUAGE_VOICES[selected_lang]["voices"]
    selected_voice_label = st.selectbox("Voice", options=list(voice_options.keys()))
    selected_voice = voice_options[selected_voice_label]

st.markdown('<div class="vx-label">03 · FINE-TUNE</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    speed = st.slider("Speed", -50, 50, 0, help="Percentage change in speaking rate")
with c2:
    pitch = st.slider("Pitch", -50, 50, 0, help="Percentage change in pitch")

rate_str = f"{'+' if speed >= 0 else ''}{speed}%"
pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.write("")
generate = st.button("🎙️  Generate Speech", type="primary", use_container_width=True)

if generate:
    if not text_input.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Synthesizing natural speech..."):
            audio_path = run_tts(text_input, selected_voice, rate_str, pitch_str)
        st.success("✅ Speech generated successfully")
        st.audio(audio_path)
        with open(audio_path, "rb") as f:
            st.download_button(
                "⬇️  Download MP3",
                data=f,
                file_name=os.path.basename(audio_path),
                mime="audio/mpeg",
                use_container_width=True,
            )
        st.session_state.history.append({
            "text": text_input[:60] + ("..." if len(text_input) > 60 else ""),
            "language": LANGUAGE_VOICES[selected_lang]["name"],
            "flag": LANGUAGE_VOICES[selected_lang]["flag"],
            "voice": selected_voice_label,
            "file": audio_path,
        })

if st.session_state.history:
    st.markdown('<div class="vx-label">GENERATION HISTORY</div>', unsafe_allow_html=True)
    for i, item in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{item['flag']}  {item['language']}  ·  {item['voice']}  —  \"{item['text']}\""):
            st.audio(item["file"])

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Vocalis · Powered by Microsoft Edge-TTS Neural Voices + langdetect · 7 languages supported")
import streamlit as st
import io
import os

_have_recorder = False
try:
    from streamlit_audiorecorder import audiorecorder  # package: streamlit-audiorecorder
    _have_recorder = True
except Exception:
    _have_recorder = False

_have_openai = False
try:
    from openai import OpenAI
    _have_openai = True
except Exception:
    _have_openai = False


def add_custom_css():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #dce9ff, #f4f7fb); font-family: 'Segoe UI', sans-serif; }
        .main-title { font-size: 48px; font-weight: 700; color: #1f5eff; text-align:center; margin-bottom: 6px; }
        .subtitle { text-align:center; color:#6c7a92; margin-bottom:18px; }
        .bubble-user { background:#b9d7ff; padding:12px; border-radius:12px; margin:8px 0; text-align:right; max-width:80%; float:right; clear:both; }
        .bubble-bot { background:#e9ecef; padding:12px; border-radius:12px; margin:8px 0; max-width:80%; float:left; clear:both; }
        .stButton>button { background:#1f5eff; color:#fff; border-radius:8px; padding:10px 18px; }
        .logo { width:72px; display:block; margin-left:auto; margin-right:auto; margin-bottom: -6px; }
        </style>
    """, unsafe_allow_html=True)

add_custom_css()


st.markdown("<img class='logo' src='https://cdn-icons-png.flaticon.com/512/1829/1829581.png'/>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title'>Solx Computer Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ask about computers — use text, upload audio, or record in your browser.</p>", unsafe_allow_html=True)


st.sidebar.title("Settings")
input_mode = st.sidebar.radio("Choose input method:", ["Text", "Upload Audio", "Record (browser)"])
st.sidebar.write("Transcription uses OpenAI Whisper if you provide an API key in Streamlit Secrets.")


def load_kb_from_file(path="data.txt"):
    kb = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    kb[k.strip().lower()] = v.strip()
                else:
                    # If no colon, store as sentence keyed by first few words
                    kb[line.strip().lower()] = line.strip()
    return kb

knowledge_base = load_kb_from_file()
if not knowledge_base:
    knowledge_base = {
        "operating system": "An OS manages hardware, memory, files, and programs.",
        "cpu": "The CPU is the brain of the computer responsible for processing instructions.",
        "ram": "RAM stores temporary data for fast access.",
        "python": "Python is a popular programming language for many tasks."
    }

def chat_bubble(text, sender="bot"):
    if sender == "user":
        st.markdown(f"<div class='bubble-user'>{st.session_state.get('user_style','')}{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-bot'>{text}</div>", unsafe_allow_html=True)

def get_kb_response(query: str):
    q = query.lower()
    for topic, answer in knowledge_base.items():
        if topic in q:
            return answer
    return ("I don't have that topic in my knowledge base yet. "
            "Try searching online: https://www.google.com/search?q=" + q.replace(" ", "+"))


def get_openai_client():
    if not _have_openai:
        return None
    key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else None
    if not key:
        return None
    try:
        return OpenAI(api_key=key)
    except Exception:
        return None

openai_client = get_openai_client()
if openai_client is None:
    st.sidebar.warning("OpenAI API key not found in Streamlit Secrets — audio transcription disabled. Add OPENAI_API_KEY to enable Whisper transcription.")

def transcribe_audio_bytes(audio_bytes, filename="audio.wav", language="en"):
    """
    Uses OpenAI Whisper via new SDK (OpenAI()) to transcribe bytes.
    Returns the transcribed text or raises Exception.
    """
    if openai_client is None:
        raise RuntimeError("OpenAI client not configured")

    
    audio_io = io.BytesIO(audio_bytes)
    audio_io.name = filename
    resp = openai_client.audio.transcriptions.create(model="whisper-1", file=audio_io)
    return resp.text

st.session_state.setdefault("history", [])

# Text mode
if input_mode == "Text":
    user_text = st.text_input("Type your computer question here:")
    if st.button("Ask"):
        if not user_text or user_text.strip() == "":
            st.warning("Please type a question.")
        else:
            st.session_state.history.append(("user", user_text))
            chat_bubble(user_text, "user")
            ans = get_kb_response(user_text)
            st.session_state.history.append(("bot", ans))
            chat_bubble(ans, "bot")

# Upload mode
elif input_mode == "Upload Audio":
    uploaded = st.file_uploader("Upload an audio file (wav, mp3, m4a)", type=["wav", "mp3", "m4a"])
    if uploaded is not None:
        st.audio(uploaded)
        if st.button("Transcribe & Ask"):
            # read bytes
            audio_bytes = uploaded.read()
            if openai_client is None:
                st.error("Audio transcription is disabled because OpenAI API key is not configured in secrets.")
            else:
                with st.spinner("Transcribing audio..."):
                    try:
                        text = transcribe_audio_bytes(audio_bytes, filename=uploaded.name)
                        st.success("Transcription complete.")
                        st.write("You said:", text)
                        st.session_state.history.append(("user", text))
                        answer = get_kb_response(text)
                        st.session_state.history.append(("bot", answer))
                        chat_bubble(text, "user")
                        chat_bubble(answer, "bot")
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

elif input_mode == "Record (browser)":
    if not _have_recorder:
        st.info("Browser recorder component not installed. You can still upload audio files or use text input.")
        st.write("To enable in-repo recording, add 'streamlit-audiorecorder' to requirements.txt and redeploy.")
        
        uploaded2 = st.file_uploader("Or upload an audio file", type=["wav", "mp3", "m4a"])
        if uploaded2 is not None:
            st.audio(uploaded2)
            if st.button("Transcribe & Ask (uploaded)"):
                if openai_client is None:
                    st.error("OpenAI API key missing — transcription disabled.")
                else:
                    try:
                        text = transcribe_audio_bytes(uploaded2.read(), filename=uploaded2.name)
                        st.write("You said:", text)
                        st.session_state.history.append(("user", text))
                        ans = get_kb_response(text)
                        st.session_state.history.append(("bot", ans))
                        chat_bubble(text, "user")
                        chat_bubble(ans, "bot")
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")
    else:
        st.write("Press record, speak, then press stop. After recording, click 'Transcribe & Ask'.")
        audio_bytes = audiorecorder("Click to record", "Stop")
        if isinstance(audio_bytes, tuple):
            
            audio_bytes = audio_bytes[0]
        if audio_bytes is not None and len(audio_bytes) > 0:
            st.audio(audio_bytes)
            if st.button("Transcribe & Ask (recorded)"):
                if openai_client is None:
                    st.error("OpenAI API key missing — transcription disabled.")
                else:
                    try:
                        text = transcribe_audio_bytes(audio_bytes, filename="recorded_audio.wav")
                        st.write("You said:", text)
                        st.session_state.history.append(("user", text))
                        ans = get_kb_response(text)
                        st.session_state.history.append(("bot", ans))
                        chat_bubble(text, "user")
                        chat_bubble(ans, "bot")
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

if st.session_state.history:
    st.markdown("---")
    st.markdown("**Conversation history (latest):**")
    for sender, msg in st.session_state.history[-10:]:
        chat_bubble(msg, "user" if sender == "user" else "bot")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#7c8aa5;'>Created by YOU - Powered by Streamlit</p>", unsafe_allow_html=True)



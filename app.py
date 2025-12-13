import streamlit as st
import os
import io

# Optional OpenAI (for voice transcription)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Computer Assistant",
    page_icon="💻",
    layout="centered"
)

# ---------- CSS ----------
st.markdown(
    """
    <style>
    .title {
        text-align:center;
        font-size:40px;
        font-weight:bold;
        color:#1f4fff;
    }
    .subtitle {
        text-align:center;
        color:#6c757d;
        margin-bottom:25px;
    }
    .user {
        background:#dbe7ff;
        padding:10px;
        border-radius:10px;
        margin:8px 0;
        text-align:right;
    }
    .bot {
        background:#eeeeee;
        padding:10px;
        border-radius:10px;
        margin:8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- HEADER ----------
st.markdown("<div class='title'>💻 Computer Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ask questions using text or voice</div>", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
def load_data():
    knowledge = {}
    if not os.path.exists("data.txt"):
        return knowledge

    with open("data.txt", "r", encoding="utf-8") as f:
        topic = None
        buffer = []

        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.isupper() and line.endswith(":"):
                if topic:
                    knowledge[topic] = " ".join(buffer)
                topic = line.replace(":", "").lower()
                buffer = []
            else:
                buffer.append(line)

        if topic:
            knowledge[topic] = " ".join(buffer)

    return knowledge

knowledge_base = load_data()

# ---------- ANSWER LOGIC ----------
def get_answer(question):
    q = question.lower()
    for topic, answer in knowledge_base.items():
        if topic in q:
            return answer
    return "I do not have this topic in my data. Please search online for more details."

# ---------- OPENAI ----------
def get_openai_client():
    if not OPENAI_AVAILABLE:
        return None
    if "OPENAI_API_KEY" not in st.secrets:
        return None
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = get_openai_client()

def transcribe_audio(audio_bytes, filename):
    if client is None:
        return None
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return result.text

# ---------- SESSION ----------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- INPUT MODE ----------
mode = st.radio("Choose input type:", ["Text", "Voice (Upload Audio)"])

# ---------- TEXT ----------
if mode == "Text":
    user_text = st.text_input("Type your question:")
    if st.button("Ask"):
        if user_text.strip():
            answer = get_answer(user_text)
            st.session_state.chat.append(("user", user_text))
            st.session_state.chat.append(("bot", answer))
        else:
            st.warning("Please type a question.")

# ---------- VOICE ----------
if mode == "Voice (Upload Audio)":
    audio = st.file_uploader(
        "Upload your voice (wav, mp3, m4a)",
        type=["wav", "mp3", "m4a"]
    )

    if audio:
        st.audio(audio)
        if st.button("Transcribe & Ask"):
            if client is None:
                st.error("OpenAI API key not set in Streamlit Secrets.")
            else:
                with st.spinner("Transcribing audio..."):
                    text = transcribe_audio(audio.read(), audio.name)
                    if text:
                        answer = get_answer(text)
                        st.session_state.chat.append(("user", text))
                        st.session_state.chat.append(("bot", answer))
                    else:
                        st.error("Could not transcribe audio.")

# ---------- DISPLAY CHAT ----------
for role, message in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot'>{message}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("Built for Streamlit Cloud")

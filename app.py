import streamlit as st
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Computer Assistant",
    page_icon="💻"
)

# ---------- CSS ----------
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #1f4fff;
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        margin-bottom: 30px;
    }
    .user {
        background-color: #dbe7ff;
        padding: 10px;
        border-radius: 10px;
        text-align: right;
        margin: 8px 0;
    }
    .bot {
        background-color: #eeeeee;
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- HEADER ----------
st.markdown("<div class='main-title'>💻 Computer Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Answers from your data.txt file</div>", unsafe_allow_html=True)

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

# ---------- CHAT ----------
def get_answer(question):
    q = question.lower()
    for topic, answer in knowledge_base.items():
        if topic in q:
            return answer
    return "Sorry, I could not find this topic in my data."

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- INPUT ----------
user_input = st.text_input("Ask a question:")

if st.button("Ask"):
    if user_input.strip():
        response = get_answer(user_input)
        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("bot", response))
    else:
        st.warning("Please type a question.")

# ---------- DISPLAY ----------
for role, msg in st.session_state.history:
    if role == "user":
        st.markdown(f"<div class='user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot'>{msg}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("Created by YOU • Streamlit Cloud")

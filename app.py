import streamlit as st
import os


st.set_page_config(
    page_title="Computer Assistant",
    page_icon="💻",
    layout="centered"
)


st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: #1f4fff;
}
.subtitle {
    text-align: center;
    color: #6c757d;
    margin-bottom: 30px;
}
.chat-user {
    background: #dbe7ff;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: right;
}
.chat-bot {
    background: #eeeeee;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
}
footer {
    text-align: center;
    color: gray;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<div class='main-title'>💻 AI Computer Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ask any basic computer-related question</div>", unsafe_allow_html=True)


def load_data(file_path="data.txt"):
    knowledge = {}
    if not os.path.exists(file_path):
        return knowledge

    with open(file_path, "r", encoding="utf-8") as f:
        current_topic = None
        content = []

        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.isupper() and line.endswith(":"):
                if current_topic:
                    knowledge[current_topic] = " ".join(content)
                current_topic = line.replace(":", "").lower()
                content = []
            else:
                content.append(line)

        if current_topic:
            knowledge[current_topic] = " ".join(content)

    return knowledge


knowledge_base = load_data()

def get_answer(question):
    q = question.lower()
    for topic, explanation in knowledge_base.items():
        if topic in q:
            return explanation

    return (
        "I don't have this topic in my knowledge base yet.\n\n"
        "Try searching online:\n"
        f"https://www.google.com/search?q={q.replace(' ', '+')}"
    )


if "history" not in st.session_state:
    st.session_state.history = []


user_input = st.text_input("Ask a computer question:")

if st.button("Ask"):
    if user_input.strip():
        answer = get_answer(user_input)
        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("bot", answer))
    else:
        st.warning("Please type a question.")


for role, message in st.session_state.history:
    if role == "user":
        st.markdown(f"<div class='chat-user'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>{message}</div>", unsafe_allow_html=True)

st.markdown("<footer>Created by YOU • Powered by Streamlit</footer>", unsafe_allow_html=True)

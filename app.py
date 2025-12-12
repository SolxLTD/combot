import streamlit as st
import speech_recognition as sr

# -----------------------------
# CUSTOM UI DESIGN
# -----------------------------
def add_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #dce9ff, #f4f7fb);
            font-family: 'Segoe UI', sans-serif;
        }
        .main-title {
            font-size: 50px;
            font-weight: bold;
            color: #1f5eff;
            text-align: center;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            color: #6c7a92;
            margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #1f5eff;
            color: white;
            border-radius: 10px;
            padding: 12px 30px;
            font-size: 18px;
            border: none;
        }
        .bubble-user {
            background-color:#b9d7ff;
            padding:12px;
            border-radius:15px;
            margin:10px 0;
            text-align:right;
            max-width:80%;
            float:right;
            clear:both;
            font-size:16px;
        }
        .bubble-bot {
            background-color:#e9ecef;
            padding:12px;
            border-radius:15px;
            margin:10px 0;
            max-width:80%;
            float:left;
            clear:both;
            font-size:16px;
        }
        .logo {
            width: 80px;
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: -10px;
        }
        </style>
    """, unsafe_allow_html=True)

add_custom_css()


def chat_bubble(text, sender="bot"):
    if sender == "user":
        st.markdown(f"<div class='bubble-user'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-bot'>{text}</div>", unsafe_allow_html=True)

st.sidebar.title("Settings")
mode = st.sidebar.radio("Select Input Type:", ["Text Input", "Voice Input"])
st.sidebar.info("Ask anything about computers!")


computer_topics = {
    "operating system": "An OS manages hardware, memory, files, and programs.",
    "cpu": "The CPU is the brain of the computer responsible for processing instructions.",
    "ram": "RAM stores temporary data for fast access while programs run.",
    "hard drive": "A hard drive stores long-term data.",
    "ssd": "An SSD is a high-speed storage device faster than HDD.",
    "python": "Python is a popular programming language.",
    "network": "Networking enables devices to communicate and share resources.",
    "ip address": "An IP address identifies a device on a network.",
    "motherboard": "The motherboard connects all computer components.",
    "gpu": "A GPU handles graphics processing."
}


def chatbot_response(user_input):
    user_input = user_input.lower()

    for topic in computer_topics:
        if topic in user_input:
            return computer_topics[topic]

    return (
        "Sorry, that topic is not in my knowledge base yet. "
        "You can search for it online: https://www.google.com/search?q=" + user_input.replace(" ", "+")
    )


def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak.")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except:
        return "Sorry, I could not understand your speech."


st.markdown("<h1 class='main-title'>AI Computer Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ask any computer question</p>", unsafe_allow_html=True)

if mode == "Text Input":
    user_text = st.text_input("Enter your question:")
    if user_text:
        chat_bubble(user_text, "user")
        reply = chatbot_response(user_text)
        chat_bubble(reply, "bot")

elif mode == "Voice Input":
    if st.button("Start Voice Input"):
        spoken_text = speech_to_text()
        chat_bubble(spoken_text, "user")
        reply = chatbot_response(spoken_text)
        chat_bubble(reply, "bot")


st.markdown("""
    <hr>
    <p style='text-align:center; color:#7c8aa5;'>
        Created by YOU - Powered by Streamlit
    </p>
""", unsafe_allow_html=True)

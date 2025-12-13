import streamlit as st
import nltk
import speech_recognition as sr
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_resource
def load_data():
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    sentences = sent_tokenize(text)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(sentences)

    return sentences, vectorizer, vectors

sentences, vectorizer, vectors = load_data()

def get_response(user_input):
    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, vectors).flatten()
    
    best_match_index = similarities.argmax()
    best_score = similarities[best_match_index]

    # If score is too low → topic not in list
    if best_score < 0.3:
        return (
            "⚠️ I don’t have information on that topic yet.\n\n"
            "You can check online:\n"
            "- Google Search: https://www.google.com/\n"
            "- Wikipedia: https://www.wikipedia.org/\n"
            "- YouTube Tutorials: https://www.youtube.com/\n\n"
            "Try asking another computer-related question!"
        )

    return sentences[best_match_index]

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception:
        return "ERROR"

st.title("💻 Smart Voice + Text Computer Chatbot")

st.write("Ask any **computer-related question**, using **text or voice**.")
st.write("If a topic is not in my database, I will refer you online.")

mode = st.radio("Choose input method:", ["Text", "Voice"])


if mode == "Text":
    user_input = st.text_input("Type your question here:")
    if st.button("Ask"):
        if user_input.strip() == "":
            st.warning("Please type something.")
        else:
            response = get_response(user_input)
            st.success(response)

else:
    st.write("Click below and speak.")
    if st.button("🎤 Start Recording"):
        transcription = speech_to_text()

        if transcription == "ERROR":
            st.error("Could not understand your voice. Try again.")
        else:
            st.write("**You said:**", transcription)
            response = get_response(transcription)
            st.success(response)

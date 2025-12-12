import streamlit as st
import speech_recognition as sr
import time


recognizer = sr.Recognizer()
mic = sr.Microphone()

# State for pause/resume
if "paused" not in st.session_state:
    st.session_state.paused = False

st.title("🎤 Improved Speech Recognition App")



# 1. Select Speech Recognition API
api_choice = st.selectbox(
    "Select Speech Recognition API:",
    [
        "Google Speech Recognition",
        "Sphinx (Offline)",
        "Google Cloud Speech",
        "Houndify",
        "IBM Speech to Text"
    ]
)

# 2. Select Language
language = st.selectbox(
    "Select Language:",
    [
        "en-US",  
        "fr-FR",  
        "es-ES",  
        "ar-SA",  
        "zh-CN", 
    ]
)

# 3. Save file toggle
save_option = st.checkbox("Save transcription to file")


def recognize_audio(audio):
    """Return text depending on API choice"""

    try:
        if api_choice == "Google Speech Recognition":
            return recognizer.recognize_google(audio, language=language)

        elif api_choice == "Sphinx (Offline)":
            return recognizer.recognize_sphinx(audio, language=language)

        elif api_choice == "Google Cloud Speech":
            return recognizer.recognize_google_cloud(audio, language=language)

        elif api_choice == "Houndify":
            return recognizer.recognize_houndify(audio)

        elif api_choice == "IBM Speech to Text":
            return recognizer.recognize_ibm(audio, language=language)

    except sr.UnknownValueError:
        return "❌ Could not understand the audio."

    except sr.RequestError:
        return "❌ API service unavailable or request failed."

    except Exception as e:
        return f"⚠ Unexpected error: {str(e)}"


def transcribe_speech():
    """Record and transcribe audio with better error handling."""

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        st.write("🎙 Listening... Speak now!")

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        except sr.WaitTimeoutError:
            return "⏳ No speech detected (timeout)."

        except Exception as e:
            return f"⚠ Error while recording: {str(e)}"

    return recognize_audio(audio)



def toggle_pause():
    st.session_state.paused = not st.session_state.paused


pause_button = st.button("⏸ Pause" if not st.session_state.paused else "▶ Resume")

if pause_button:
    toggle_pause()



if not st.session_state.paused:

    if st.button("Start Recording"):
        text = transcribe_speech()

        st.subheader("📝 Transcription Result:")
        st.write(text)

        # Save the output
        if save_option and text.strip():
            filename = f"transcription_{int(time.time())}.txt"
            with open(filename, "w") as f:
                f.write(text)
            st.success(f"📁 File saved: {filename}")

else:
    st.info("Recording paused. Click Resume to continue.")

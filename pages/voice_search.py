import speech_recognition as sr

def listen_voice():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=5
            )

        text = recognizer.recognize_google(
            audio
        )

        return text

    except Exception:

        return ""
import streamlit as st
import pandas as pd
import sqlite3
import speech_recognition as sr

# -------------------------------------
# PAGE CONFIG
# -------------------------------------
st.set_page_config(
    page_title="Voice Search",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 AI Voice Product Search")
st.caption("Search inventory products using your voice.")

# -------------------------------------
# DATABASE
# -------------------------------------
conn = sqlite3.connect(
    "inventory.db",
    check_same_thread=False
)

products_df = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

# -------------------------------------
# VOICE RECOGNITION FUNCTION
# -------------------------------------
def listen_to_voice():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        st.info("🎙 Listening... Please speak now.")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        audio = recognizer.listen(
            source,
            timeout=5
        )

    try:

        text = recognizer.recognize_google(
            audio
        )

        return text

    except sr.UnknownValueError:
        return None

    except sr.RequestError:
        return None

# -------------------------------------
# VOICE BUTTON
# -------------------------------------
if st.button("🎤 Start Voice Search"):

    voice_text = listen_to_voice()

    if voice_text:

        st.success(
            f"Recognized: {voice_text}"
        )

        search_term = voice_text.lower()

        results = products_df[
            products_df["name"]
            .str.lower()
            .str.contains(
                search_term,
                na=False
            )
        ]

        if not results.empty:

            st.subheader(
                "📦 Matching Products"
            )

            st.dataframe(
                results,
                use_container_width=True
            )

        else:

            st.warning(
                "No matching product found."
            )

    else:

        st.error(
            "Could not understand voice input."
        )

# -------------------------------------
# MANUAL SEARCH BACKUP
# -------------------------------------
st.divider()

st.subheader("🔍 Manual Search")

query = st.text_input(
    "Enter Product Name"
)

if query:

    results = products_df[
        products_df["name"]
        .str.contains(
            query,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        results,
        use_container_width=True
    )

# -------------------------------------
# INVENTORY OVERVIEW
# -------------------------------------
st.divider()

st.subheader("📋 Available Products")

st.dataframe(
    products_df,
    use_container_width=True
)

conn.close()
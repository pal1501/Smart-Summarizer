import streamlit as st
import openai
import whisper
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Set your OpenAI API key securely
openai.api_key = os.getenv("SummarizerAPI_KEY")

# Load Whisper model (you can change to 'medium' or 'large' if needed)
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

st.title("🤖 Smart Meeting Notes Summarizer")
st.write("Upload your meeting audio or transcript to get a summary, action items, and decisions.")

# Ensure the 'uploads' directory exists
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# File uploader
uploaded_file = st.file_uploader("Upload meeting audio (.mp3/.wav) or transcript (.txt)", type=["mp3", "wav", "txt"])

if uploaded_file:
    file_path = os.path.join(upload_dir, uploaded_file.name)
    
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' successfully uploaded to {file_path}")
    except Exception as e:
        st.error(f"Error saving file: {e}")

    # Process transcript
    if uploaded_file.name.endswith(".txt"):
        transcript = uploaded_file.getvalue().decode("utf-8")  # Convert bytes to string
        st.success("Transcript loaded successfully.")

    # Process audio
    else:
        st.info("Transcribing audio with Whisper model...")
        result = model.transcribe(file_path)
        transcript = result["text"]
        st.success("Transcription complete!")

    # Show transcript (optional)
    with st.expander("📄 View Transcript"):
        st.write(transcript)

    # Summarize with Gemini
    st.info("Summarizing with Gemini...")
    prompt = f"""
    You are a helpful meeting summarizer.
    Here's the transcript of a meeting:

    {transcript}

    Extract and format:
    1. Key Discussion Points
    2. Action Items
    3. Decisions Made
    """

    import requests
    GEMINI_API_KEY = "AIzaSyA8fmTON2w1xKaF5peKTEok8BSyJpWdPq4"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
    "contents": [{"parts": [{"text": f"Summarize the following transcript: {transcript}"}]}]
    }


    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())

    response_json = response.json()  # Convert response to JSON
    summary = response_json["candidates"][0]["content"]
    '''
    import json
    with open("summary.txt", "w") as out:
        out.write(json.dumps(summary, indent=4))  # Converts dict to JSON string
    
    print(summary)  # See what type of data it contains
    print(type(summary))  # Confirm if it's a dict
    '''


    st.subheader("📋 Meeting Summary")
    st.write(summary)

    # Optional: Save output
    import json
    with open("output_summary.txt", "w", encoding="utf-8") as out:
        out.write(json.dumps(summary, indent=4))

    st.download_button("Download Summary", json.dumps(summary, indent=4), file_name="meeting_summary.txt")



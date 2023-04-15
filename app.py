import os
import sys
import datetime
import openai

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

import streamlit as st

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript

def clean_transcription(transcription):
    prompt = "Eres un secretario. Tu función es pasar en limpio las notas transcritas. El texto resultante debe ordenar ideas y ampliar o reducir cuando sea necesario. El hecho es que el usuario debe poder decir al leer las notas que tú elaboras: 'Justamente, esto es lo que quería decir'"

    model_engine = "text-davinci-003"
    max_tokens = 1024
    temperature = 0.7

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt + "\n" + transcription,
        max_tokens=max_tokens,
        temperature=temperature
    )

    clean_text = response.choices[0].text
    return clean_text

st.title("Whisper Transcription")

# tab record audio and upload audio
tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180.0, sample_rate=41_000)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

with tab2:
    audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        # st.audio(audio_file.read(), format={audio_file.type})
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # save audio file with correct extension
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

if st.button("Transcribe"):
    # find newest audio file
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )

    # transcribe
    audio_file = open(audio_file_path, "rb")

    transcript = transcribe(audio_file)
    text = transcript["text"]

    # clean and order transcript
    cleaned_text = clean_transcription(text)

    st.header("Transcript")
    st.write(cleaned_text)

    # save transcript to text file
    with open("transcript.txt", "w") as f:
        f.write(cleaned_text)

    # download transcript
    st.download_button('Download Transcript', cleaned_text)
def clean_transcription(transcription):
    prompt = (f"Eres un secretario. Tu función es pasar en limpio las notas transcritas. El texto resultante debe "
              f"ordenar ideas y ampliar o reducir cuando sea necesario. El hecho es que el usuario debe poder decir "
              f"al leer las notas que tú elaboras: 'justamente, esto es lo que quería decir'.\n\n"
              f"Transcripción:\n{transcription}\n\nTexto final:")

    # Limpiar y ordenar transcripción con OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Obtener el texto final
    text = response.choices[0].text

    # Eliminar el prompt y devolver el texto final
    return text.split("Texto final:")[1].strip()

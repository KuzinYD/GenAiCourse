import os
import io
import hashlib
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types
from utils.logger_helper import get_logger
from pydub import AudioSegment

# ===========================
# Config
# ===========================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

TEXT_MODEL = os.getenv("TEXT_MODEL")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
ASR_MODEL = os.getenv("ASR_MODEL")

MAX_DURATION = 10  # seconds
OUTPUT_BITRATE = "128k"

logger = get_logger(__name__)
logger.info("🚀 App initialized.")
logger.info(f"Using models: ASR={ASR_MODEL}, TEXT={TEXT_MODEL}, IMAGE={IMAGE_MODEL}")

client = genai.Client(api_key=API_KEY)
logger.info("Gemini client initialized.")

# ===========================
# UI
# ===========================
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This app demonstrates a voice-to-image generation pipeline using Google Gemini models.
    - Record your voice describing an image.
    - The audio is transcribed using an ASR model.
    - The transcription is rewritten into a detailed image prompt.
    - An image is generated based on the prompt.
    """)
    st.markdown(f"**Models used:**\n- ASR: {ASR_MODEL}\n- Text: {TEXT_MODEL}\n- Image: {IMAGE_MODEL}")

    st.divider()

st.set_page_config(page_title="Voice → Image", layout="centered")
st.title("🎤 Voice → 🎨 Image")
st.caption("Record audio → transcribe → rewrite → generate image.")
st.write("---")
logger.info("UI rendered.")

# ===========================
# Audio Input
# ===========================
logger.info("Waiting for audio input...")
audio_data = st.audio_input("🎙 Click to record audio", label_visibility="visible")

if audio_data is not None:
    logger.info("Audio input received!")

    # Read bytes
    try:
        raw = audio_data.getvalue()
        logger.debug(f"Audio raw bytes length: {len(raw)}")
    except Exception as e:
        logger.exception("Failed to read audio bytes")
        st.error("Failed to read audio bytes.")
        st.stop()

    # Hash for debugging
    audio_hash = hashlib.sha256(raw).hexdigest()
    logger.info(f"Audio SHA-256 hash: {audio_hash}")

    # ===========================
    # Duration + Re-encoding with pydub
    # ===========================
    logger.info(f"Decoding with pydub (MIME={audio_data.type})...")

    try:
        audio = AudioSegment.from_file(io.BytesIO(raw), format=audio_data.type.split("/")[-1])
    except Exception as e:
        logger.exception("Pydub failed to read audio.")
        st.error(f"Could not decode audio: {e}")
        st.stop()

    duration = audio.duration_seconds
    logger.info(f"Duration detected: {duration:.2f} seconds")

    # Enforce max length
    if duration > MAX_DURATION:
        logger.warning(f"Audio too long ({duration:.2f}s). Trimming to 10s.")
        st.markdown(f"Audio too long ({duration:.2f}s). Trimming to 10s.")

        # Auto-trim
        audio = audio[: MAX_DURATION * 1000]  # milliseconds
        duration = MAX_DURATION

    # Re-encode at clean MP3 128k
    logger.info("Re-encoding audio at 128kbps MP3...")
    output_mp3 = io.BytesIO()
    audio.export(output_mp3, format="mp3", bitrate=OUTPUT_BITRATE)
    processed_audio_bytes = output_mp3.getvalue()

    logger.info(f"Processed audio length: {len(processed_audio_bytes)} bytes")

    # Convert to Gemini Part
    try:
        audio_part = types.Part.from_bytes(data=processed_audio_bytes, mime_type="audio/mp3")
        logger.info("Audio Part for Gemini created successfully.")
    except Exception as e:
        logger.exception("Failed to convert to Gemini Part.")
        st.error(f"❌ Failed to prepare audio for model: {e}")
        st.stop()

    # Optional waveform preview:
    # st.audio(processed_audio_bytes, format="audio/mp3")

    # =====================================================================
    # 1. ASR
    # =====================================================================
    logger.info("Starting ASR transcription...")
    with st.spinner("Transcribing speech..."):
        try:
            asr_resp = client.models.generate_content(
                model=ASR_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction="Transcribe this audio clearly."
                ),
                contents=[audio_part],
            )
            transcription = asr_resp.text.strip()
            logger.info(f"ASR transcription: {transcription}")
        except Exception as e:
            logger.exception("ASR failed.")
            st.error(f"ASR failed: {e}")
            st.stop()

    st.markdown(f"**📝 Transcription:** {transcription}")

    # =====================================================================
    # 2. Rewrite Prompt
    # =====================================================================
    logger.info("Rewriting transcription into an image prompt...")

    with st.spinner("Rewriting into an image prompt..."):
        try:
            rewrite_resp = client.models.generate_content(
                model=TEXT_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction="Rewrite the following user request into a single, detailed image-generation prompt suitable for an image model. Keep it short."
                ),
                contents=[transcription],
            )
            rewritten_prompt = rewrite_resp.text.strip()
            logger.info(f"Rewritten prompt: {rewritten_prompt}")
        except Exception as e:
            logger.exception("Prompt rewrite failed.")
            st.error(f"❌ Error rewriting prompt: {e}")
            st.stop()

    st.success("🎯 Prepared prompt: " + rewritten_prompt)

    # =====================================================================
    # 3. Generate Image
    # =====================================================================
    logger.info("Generating image from rewritten prompt...")

    with st.spinner("Generating image..."):
        image_bytes = None

        try:
            img_resp = client.models.generate_content(model=IMAGE_MODEL, contents=[rewritten_prompt])
            logger.debug(f"Image model response: {img_resp}")

            for p in img_resp.parts:
                if p.inline_data:
                    image_bytes = p.inline_data.data
                    logger.info(f"Image bytes received: {len(image_bytes)}")
                    break

        except Exception as e:
            logger.exception("Image generation failed.")
            st.error(f"Image generation failed: {e}")
            st.stop()

    # =====================================================================
    # 4. Display Image
    # =====================================================================
    if image_bytes:
        logger.info("Displaying image.")
        st.image(image_bytes, caption="🎨 Generated Image")
    else:
        logger.warning("No image returned.")
        st.warning("No image returned from model.")

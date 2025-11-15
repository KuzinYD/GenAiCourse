import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
from io import BytesIO

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")

client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Voice to Image", layout="centered")
st.title("Voice to Image")
st.subheader("Generate an image from your prompt")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Tell me what image to generate."}
    ]

def display_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("image"):
                st.image(msg["image"], caption="Generated image")
            else:
                st.write(msg["content"])

display_messages()

prompt = st.chat_input("Type a prompt to generate an image...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("🎨 Generating image...")

        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=[prompt],
            )


            generated_image_bytes = None
            response_text = ""

            for part in response.parts:
                if part.text is not None:
                    response_text += part.text + "\n"

                elif part.inline_data is not None:
                    # DIRECT PNG BYTES (best and safest)
                    generated_image_bytes = part.inline_data.data

            if generated_image_bytes:
                placeholder.image(generated_image_bytes, caption="Generated image")

                st.session_state.messages.append({
                    "role": "assistant",
                    "image": generated_image_bytes
                })
            else:
                placeholder.write(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })


        except Exception as e:
            error_msg = f"❌ Error: {e}"
            placeholder.write(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

    st.rerun()

# Voice-to-Image Generation App

A Streamlit application that demonstrates a complete voice-to-image generation pipeline using Google Gemini models. This Capstone II project showcases the integration of multiple AI capabilities: Automatic Speech Recognition (ASR), text processing, and image generation.

## Features

🎤 **Voice Input** - Record audio descriptions through your browser  
📝 **Speech Transcription** - Convert speech to text using Google's ASR model  
✍️ **Prompt Enhancement** - Rewrite transcriptions into detailed image prompts  
🎨 **Image Generation** - Create images from enhanced prompts using Gemini

## Contents

- `app.py` — Main Streamlit application
- `requirements.txt` — Python dependencies
- `utils/logger_helper.py` — Logging utility module
- `.env` — Environment variables (create this file)

## Prerequisites

1. **Google API Key**: You'll need a Google AI API key with access to Gemini models
2. **Python 3.8+**: Required for all dependencies
3. **Audio recording capability**: Browser microphone access

## Setup Instructions

1. **Clone and navigate to the project:**

   ```bash
   cd /path/to/capstone_ii
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   TEXT_MODEL=gemini-1.5-flash
   IMAGE_MODEL=imagen-3.0-generate-001
   ASR_MODEL=gemini-1.5-flash
   ```

5. **Run the application:**

   ```bash
   streamlit run app.py
   ```

6. **Access the app:**
   Open your browser to `http://localhost:8501`

## How to Use

1. **Record Audio**: Click the microphone button and describe the image you want to generate
2. **Wait for Processing**: The app will automatically:
   - Transcribe your speech
   - Enhance the description into a detailed prompt
   - Generate an image based on the prompt
3. **View Results**: See your transcription, enhanced prompt, and generated image

## Technical Details

- **Audio Processing**: Supports various audio formats, automatically trims to 10 seconds max
- **Model Pipeline**: ASR → Text Enhancement → Image Generation
- **Audio Encoding**: Converts audio to MP3 at 128kbps for optimal processing
- **Logging**: Comprehensive logging for debugging and monitoring


## Environment Variables

| Variable         | Description                         | Example                   |
| ---------------- | ----------------------------------- | ------------------------- |
| `GOOGLE_API_KEY` | Your Google AI API key              | `AIza...`                 |
| `TEXT_MODEL`     | Gemini model for text processing    | `gemini-1.5-flash`        |
| `IMAGE_MODEL`    | Gemini model for image generation   | `imagen-3.0-generate-001` |
| `ASR_MODEL`      | Gemini model for speech recognition | `gemini-1.5-flash`        |

## Project Goals

- Demonstrate end-to-end AI pipeline integration
- Showcase multi-modal AI capabilities (audio, text, image)
- Provide practical experience with Google Gemini models
- Create an intuitive user interface for complex AI workflows

## Troubleshooting

- **API Errors**: Verify your Google API key and model access
- **Audio Issues**: Ensure browser microphone permissions are granted
- **Long Processing**: Audio is limited to 10 seconds for optimal performance
- **Dependencies**: Run `pip install -r requirements.txt` if imports fail

## Contributing

Feel free to open issues or pull requests. Please:

- Keep changes focused and well-documented
- Test thoroughly before submitting
- Follow the existing code style

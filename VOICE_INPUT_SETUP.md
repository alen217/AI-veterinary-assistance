# Voice Input Setup Guide for AVA

## 📋 Overview

AVA now supports **voice input** for patient descriptions! You can record your voice in **English** or **Malayalam** and it will automatically convert to text. This is powered by OpenAI's Whisper model, which provides excellent accuracy for medical terminology.

---

## 🎯 Features

- ✅ **English Speech-to-Text** - Full support
- ✅ **Malayalam Speech-to-Text** - Full support with optional translation to English
- ✅ **Sentence-by-sentence transcription** - See your speech broken down by sentences
- ✅ **Auto-detection** - Can automatically detect the language being spoken
- ✅ **Offline processing** - Works without internet (after initial setup)
- ✅ **Medical terminology support** - Good accuracy with veterinary terms

---

## 📦 Installation Steps

### Step 1: Install Required Packages

Open PowerShell in your project directory and run:

```powershell
# Install OpenAI Whisper for speech recognition
pip install openai-whisper

# Install audio recorder for Streamlit
pip install audio-recorder-streamlit

# Update other dependencies
pip install -r requirements.txt
```

### Step 2: Install FFmpeg (Required for Audio Processing)

Whisper requires FFmpeg to process audio files.

#### Windows Installation:

1. **Download FFmpeg:**
   - Go to https://www.gyan.dev/ffmpeg/builds/
   - Download `ffmpeg-release-essentials.zip`

2. **Extract and Add to PATH:**
   ```powershell
   # Extract to a permanent location (e.g., C:\ffmpeg)
   # Then add to PATH:
   $env:Path += ";C:\ffmpeg\bin"
   
   # To make it permanent, add to system PATH:
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
   ```

3. **Verify Installation:**
   ```powershell
   ffmpeg -version
   ```

#### Linux Installation:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### Mac Installation:
```bash
brew install ffmpeg
```

### Step 3: Download Whisper Model (First Run)

The first time you use voice input, Whisper will automatically download the model. This happens in the background and takes a few minutes.

**Model sizes available:**
- `tiny` - 39M parameters, fastest, less accurate
- `base` - 74M parameters, **default choice**, good balance
- `small` - 244M parameters, better accuracy
- `medium` - 769M parameters, even better
- `large` - 1550M parameters, best accuracy (slowest)

AVA uses the `base` model by default for a good balance.

---

## 🚀 Usage

### In the Streamlit App:

1. **Navigate to Diagnosis Page**
   - Click "🔍 Diagnosis" in the sidebar

2. **Open Voice Input**
   - Click on "🎤 Voice Input - Speak your patient description" expander

3. **Select Language**
   - Choose "English" or "Malayalam"
   - If Malayalam, you can optionally translate to English

4. **Record Your Voice**
   - Click the microphone button to start recording
   - Speak clearly about the patient's symptoms
   - Click the microphone button again to stop

5. **Review Transcription**
   - The transcription appears below the recorder
   - You can see sentence-by-sentence breakdown

6. **Add to Description**
   - Click "➕ Add to Description" to append to existing text
   - Or click "🔄 Replace Description" to replace all text

### Example Use Cases:

#### English Example:
```
"My three year old golden retriever has been coughing for about a week. 
He seems very lethargic and has a fever of 103 degrees. 
His breathing sounds labored sometimes, especially after walking. 
He's been fully vaccinated and has no prior health issues."
```

#### Malayalam Example (with translation):
```
"എന്റെ നായ്ക്കുട്ടിക്ക് ഒരു ആഴ്ചയായി ചുമയുണ്ട്. 
അവന് ക്ഷീണം തോന്നുന്നു, പനിയുമുണ്ട്."
```
*(Will be translated to English for better analysis)*

---

## ⚙️ Advanced Configuration

### Changing Model Size

If you need better accuracy or faster processing, you can modify the model size in [voice_input.py](voice_input.py):

```python
# For faster processing (less accurate):
transcribed_text = render_voice_input_widget(
    model_size="tiny"  # or "small"
)

# For better accuracy (slower):
transcribed_text = render_voice_input_widget(
    model_size="medium"  # or "large"
)
```

### Supported Languages

Whisper supports 99+ languages including:
- English (en)
- Malayalam (ml)
- Hindi (hi)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- Bengali (bn)
- And many more...

To add more language options, edit [app_streamlit.py](app_streamlit.py) around line 594:

```python
voice_lang = st.radio(
    "Select Language",
    options=["English", "Malayalam", "Hindi", "Tamil"],  # Add more
    horizontal=True,
    key="voice_lang_select"
)
```

---

## 🔧 Troubleshooting

### Problem: "Whisper not installed" error

**Solution:**
```powershell
pip install openai-whisper
```

### Problem: "ffmpeg not found" error

**Solution:**
- Make sure FFmpeg is installed and in your PATH
- Restart your terminal/PowerShell after installation
- Test with: `ffmpeg -version`

### Problem: Voice input widget not showing

**Solution:**
```powershell
pip install audio-recorder-streamlit
streamlit cache clear
```

### Problem: Model download is slow

**Solution:**
- This is normal for the first time (model is ~150MB for base)
- Subsequent uses will be fast as the model is cached
- Consider using a smaller model like "tiny" for testing

### Problem: Low accuracy in Malayalam

**Solution:**
- Enable "Translate to English" option
- This uses Whisper's translation feature for better medical terminology
- English analysis provides better diagnostic accuracy

### Problem: GPU not being used (slow processing)

**Solution:**
```powershell
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# If False, install CUDA-enabled PyTorch:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 🎤 Best Practices for Voice Recording

1. **Speak Clearly** - Enunciate medical terms
2. **Reduce Background Noise** - Find a quiet environment
3. **Use Complete Sentences** - This helps with context
4. **Pause Between Thoughts** - Helps with sentence segmentation
5. **Review Before Adding** - Check the transcription for accuracy
6. **Multiple Recordings** - You can record and add multiple times
7. **Edit After Adding** - You can still manually edit the text

---

## 📊 Performance Expectations

| Model Size | Speed    | Accuracy | File Size |
|------------|----------|----------|-----------|
| Tiny       | Fastest  | Good     | ~39 MB    |
| **Base**   | Fast     | **Good** | ~74 MB    |
| Small      | Medium   | Better   | ~244 MB   |
| Medium     | Slow     | Best     | ~769 MB   |
| Large      | Slowest  | Best     | ~1550 MB  |

**Recommended:** Use `base` model (default) for most cases.

---

## 🔒 Privacy & Security

- ✅ **100% Offline** - All processing happens on your computer
- ✅ **No Cloud API** - No data sent to external servers
- ✅ **No Recording Storage** - Audio is processed and immediately discarded
- ✅ **Local Models** - Whisper model runs locally

---

## 🆘 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Verify all dependencies are installed:
   ```powershell
   pip list | Select-String "whisper|audio-recorder"
   ffmpeg -version
   ```
3. Check the console output for detailed error messages
4. Try with a smaller model size first (`tiny`)

---

## 🎉 What's Next?

Voice input is now fully integrated! You can:
- Record patient symptoms in your preferred language
- Use it alongside manual text entry
- Combine multiple voice recordings
- Edit the transcription before analysis

Enjoy the convenience of hands-free patient data entry! 🐾

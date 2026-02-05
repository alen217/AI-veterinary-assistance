"""
Voice Input Module for AVA - Veterinary AI Assistant
Supports English and Malayalam speech-to-text conversion using OpenAI Whisper
"""

import streamlit as st
import os
import tempfile
import torch
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False


class VoiceInputHandler:
    """
    Handles voice input recording and speech-to-text conversion
    Supports English and Malayalam languages
    """
    
    def __init__(self, model_size="base", default_language="en"):
        """
        Initialize the voice input handler
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
                       - tiny: fastest, least accurate
                       - base: good balance (recommended)
                       - small: better accuracy
                       - medium/large: best accuracy but slower
            default_language: Default language code ("en" for English, "ml" for Malayalam)
        """
        self.model_size = model_size
        self.default_language = default_language
        self.model = None
        
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "Whisper not installed. Install with: pip install openai-whisper"
            )
    
    def load_model(self):
        """Load the Whisper model (lazy loading)"""
        if self.model is None:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = whisper.load_model(self.model_size, device=device)
                return True
            except Exception as e:
                st.error(f"Failed to load Whisper model: {e}")
                return False
        return True
    
    def transcribe_audio(self, audio_bytes, language="en"):
        """
        Transcribe audio bytes to text
        
        Args:
            audio_bytes: Audio data in bytes format
            language: Language code ("en" for English, "ml" for Malayalam, or None for auto-detect)
        
        Returns:
            dict with 'text', 'language', 'segments' (sentence-by-sentence)
        """
        if not self.load_model():
            return {"text": "", "language": "", "segments": [], "error": "Model loading failed"}
        
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe with Whisper
            options = {
                "language": language if language != "auto" else None,
                "task": "transcribe",  # or "translate" to translate to English
                "fp16": False  # Use FP32 for CPU compatibility
            }
            
            result = self.model.transcribe(tmp_path, **options)
            
            # Extract sentence-by-sentence segments
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip()
                })
            
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", language),
                "segments": segments,
                "error": None
            }
        
        except Exception as e:
            return {
                "text": "",
                "language": language,
                "segments": [],
                "error": str(e)
            }
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def translate_to_english(self, audio_bytes):
        """
        Translate any language audio to English
        Useful for Malayalam to English translation
        
        Args:
            audio_bytes: Audio data in bytes format
        
        Returns:
            dict with translated 'text' in English
        """
        if not self.load_model():
            return {"text": "", "error": "Model loading failed"}
        
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Use "translate" task to convert to English
            result = self.model.transcribe(
                tmp_path,
                task="translate",  # This translates to English
                fp16=False
            )
            
            return {
                "text": result.get("text", "").strip(),
                "source_language": result.get("language", "unknown"),
                "error": None
            }
        
        except Exception as e:
            return {
                "text": "",
                "error": str(e)
            }
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass


def render_voice_input_widget(
    key="voice_input",
    language="en",
    show_segments=True,
    translate_to_english=False,
    model_size="base"
):
    """
    Render a voice input widget in Streamlit
    
    Args:
        key: Unique key for the widget
        language: Language for transcription ("en", "ml", or "auto")
        show_segments: Whether to show sentence-by-sentence segments
        translate_to_english: If True, translate Malayalam/other languages to English
        model_size: Whisper model size
    
    Returns:
        Transcribed text or None if no recording
    """
    
    if not WHISPER_AVAILABLE:
        st.error("⚠️ Voice input requires OpenAI Whisper. Install with:\n```bash\npip install openai-whisper\n```")
        return None
    
    if not AUDIO_RECORDER_AVAILABLE:
        st.error("⚠️ Voice input requires audio recorder. Install with:\n```bash\npip install audio-recorder-streamlit\n```")
        return None
    
    # Language selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**🎤 Voice Input**")
    with col2:
        lang_option = st.selectbox(
            "Language",
            options=["English", "Malayalam", "Auto-detect"],
            index=0 if language == "en" else (1 if language == "ml" else 2),
            key=f"{key}_lang"
        )
    
    # Map language option to code
    lang_code_map = {
        "English": "en",
        "Malayalam": "ml",
        "Auto-detect": "auto"
    }
    selected_lang = lang_code_map.get(lang_option, "en")
    
    # Optional: Translate to English checkbox (useful for Malayalam)
    if selected_lang == "ml":
        translate_to_english = st.checkbox(
            "Translate to English",
            value=translate_to_english,
            key=f"{key}_translate",
            help="Convert Malayalam speech to English text"
        )
    
    # Audio recorder
    st.info("👇 Click the microphone button to start recording, click again to stop")
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="2x",
        key=f"{key}_recorder"
    )
    
    if audio_bytes:
        # Initialize handler
        if f"{key}_handler" not in st.session_state:
            with st.spinner("Loading speech recognition model..."):
                st.session_state[f"{key}_handler"] = VoiceInputHandler(
                    model_size=model_size,
                    default_language=selected_lang
                )
        
        handler = st.session_state[f"{key}_handler"]
        
        # Transcribe audio
        with st.spinner("🔄 Converting speech to text..."):
            if translate_to_english and selected_lang == "ml":
                result = handler.translate_to_english(audio_bytes)
                transcription = result.get("text", "")
                if result.get("error"):
                    st.error(f"❌ Translation error: {result['error']}")
                    return None
                else:
                    st.success(f"✅ Translated from {result.get('source_language', 'Malayalam')} to English")
            else:
                result = handler.transcribe_audio(audio_bytes, language=selected_lang)
                transcription = result.get("text", "")
                
                if result.get("error"):
                    st.error(f"❌ Transcription error: {result['error']}")
                    return None
                else:
                    detected_lang = result.get("language", selected_lang)
                    st.success(f"✅ Transcribed ({detected_lang.upper()})")
            
            # Display transcription
            if transcription:
                st.markdown("**Transcription:**")
                st.text_area(
                    label="",
                    value=transcription,
                    height=100,
                    key=f"{key}_output",
                    label_visibility="collapsed"
                )
                
                # Show segments if requested
                if show_segments and not translate_to_english and result.get("segments"):
                    with st.expander("📝 View sentence-by-sentence"):
                        for i, segment in enumerate(result["segments"], 1):
                            st.write(f"**{i}.** {segment['text']}")
                            st.caption(f"Time: {segment['start']:.1f}s - {segment['end']:.1f}s")
                
                return transcription
            else:
                st.warning("⚠️ No speech detected. Please try again.")
                return None
    
    return None


def render_voice_input_button(
    text_area_key,
    language="en",
    append_mode=True,
    model_size="base"
):
    """
    Render a voice input button that adds text to an existing text area
    
    Args:
        text_area_key: The key of the text area to append to
        language: Language for transcription
        append_mode: If True, append to existing text; if False, replace
        model_size: Whisper model size
    """
    
    if not WHISPER_AVAILABLE:
        st.warning("⚠️ Voice input not available. Install with: `pip install openai-whisper`")
        return
    
    if not AUDIO_RECORDER_AVAILABLE:
        st.warning("⚠️ Audio recorder not available. Install with: `pip install audio-recorder-streamlit`")
        return
    
    # Create a unique key for this voice input session
    voice_key = f"voice_{text_area_key}"
    
    # Render voice input widget
    with st.expander("🎤 Voice Input", expanded=False):
        transcription = render_voice_input_widget(
            key=voice_key,
            language=language,
            show_segments=True,
            model_size=model_size
        )
        
        if transcription:
            # Add button to insert transcription
            if st.button("➕ Add to Description", key=f"{voice_key}_add"):
                if text_area_key in st.session_state:
                    current_text = st.session_state[text_area_key]
                    if append_mode and current_text:
                        st.session_state[text_area_key] = current_text + " " + transcription
                    else:
                        st.session_state[text_area_key] = transcription
                    st.success("✅ Voice input added to description!")
                    st.rerun()

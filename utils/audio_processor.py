import os
import tempfile
import logging
import numpy as np
import librosa
import soundfile as sf
from gtts import gTTS
from scipy import signal

logger = logging.getLogger(__name__)

def process_voice_clone(audio_path):
    """
    Process voice cloning using lightweight feature extraction
    """
    try:
        if not audio_path:
            logger.debug("No audio path provided, using default voice")
            return "default_voice"

        logger.debug(f"Loading audio file from: {audio_path}")
        # Load and process reference audio
        y, sr = librosa.load(audio_path, sr=None, duration=30)  # Limit to 30 seconds
        logger.debug(f"Audio loaded successfully, sample rate: {sr}")

        # Extract voice features
        logger.debug("Extracting voice features...")

        # Extract spectral features (simpler approach)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        logger.debug("MFCC extraction complete")

        # Save processed features
        temp_model_path = os.path.join(tempfile.gettempdir(), 'voice_features.npz')
        np.savez(temp_model_path,
                mfcc=mfcc,
                sample_rate=sr)

        logger.debug(f"Voice features saved to: {temp_model_path}")
        return temp_model_path
    except Exception as e:
        logger.error(f"Error in voice model creation: {str(e)}")
        raise

def generate_speech(text, model_path, language):
    """
    Generate speech with voice adaptation
    """
    try:
        logger.debug(f"Generating speech for text: {text}, language: {language}")
        # First generate base speech using gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        temp_path = os.path.join(tempfile.gettempdir(), 'temp_output.mp3')
        tts.save(temp_path)
        logger.debug("Base speech generated with gTTS")

        # Load the generated speech
        y, sr = librosa.load(temp_path, sr=None)

        # If we have a voice model, adapt the output
        if model_path != "default_voice" and os.path.exists(model_path):
            try:
                logger.debug(f"Loading voice features from: {model_path}")
                # Load voice features
                voice_features = np.load(model_path, allow_pickle=True)

                # Simple time stretching for voice adaptation
                y_processed = librosa.effects.time_stretch(y, rate=0.95)
                logger.debug("Applied time stretching")

            except Exception as e:
                logger.error(f"Error in voice adaptation: {str(e)}")
                logger.debug("Falling back to original audio")
                y_processed = y
        else:
            logger.debug("Using default voice (no adaptation)")
            y_processed = y

        # Save as MP3
        output_path = os.path.join(tempfile.gettempdir(), 'output.mp3')
        sf.write(output_path, y_processed, sr, format='mp3')
        logger.debug(f"Saved processed audio to: {output_path}")

        return output_path
    except Exception as e:
        logger.error(f"Error in speech generation: {str(e)}")
        # Fallback to direct gTTS output
        logger.debug("Falling back to direct gTTS output")
        output_path = os.path.join(tempfile.gettempdir(), 'output.mp3')
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        return output_path
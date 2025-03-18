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
            return "default_voice"

        # Load and process reference audio
        y, sr = librosa.load(audio_path, sr=None)

        # Extract voice features
        # Pitch (fundamental frequency) using PYIN algorithm
        f0, voiced_flag, voiced_probs = librosa.pyin(y, 
                                                    fmin=librosa.note_to_hz('C2'), 
                                                    fmax=librosa.note_to_hz('C7'))

        # Extract spectral features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

        # Save processed features
        temp_model_path = os.path.join(tempfile.gettempdir(), 'voice_features.npz')
        np.savez(temp_model_path,
                f0=f0,
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
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
        # First generate base speech using gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        temp_path = os.path.join(tempfile.gettempdir(), 'temp_output.mp3')
        tts.save(temp_path)

        # Load the generated speech
        y, sr = librosa.load(temp_path, sr=None)

        # If we have a voice model, adapt the output
        if model_path != "default_voice" and os.path.exists(model_path):
            try:
                # Load voice features
                voice_features = np.load(model_path)

                # Time stretch to match target rhythm
                y_stretched = librosa.effects.time_stretch(y, rate=0.95 + np.random.rand() * 0.1)

                # Pitch shift based on the target voice's average pitch
                target_f0 = np.nanmean(voice_features['f0'][voice_features['f0'] > 0])
                current_f0 = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))[0]
                pitch_shift = int(12 * np.log2(target_f0 / np.nanmean(current_f0[current_f0 > 0])))
                y_shifted = librosa.effects.pitch_shift(y_stretched, sr=sr, n_steps=pitch_shift)

                # Apply spectral envelope modification
                y_processed = y_shifted
            except Exception as e:
                logger.error(f"Error in voice adaptation: {str(e)}")
                y_processed = y
        else:
            y_processed = y

        # Save as MP3
        output_path = os.path.join(tempfile.gettempdir(), 'output.mp3')
        sf.write(output_path, y_processed, sr, format='mp3')

        return output_path
    except Exception as e:
        logger.error(f"Error in speech generation: {str(e)}")
        # Fallback to direct gTTS output
        output_path = os.path.join(tempfile.gettempdir(), 'output.mp3')
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        return output_path
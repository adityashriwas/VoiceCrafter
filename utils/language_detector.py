from langdetect import detect
import logging

logger = logging.getLogger(__name__)

def detect_language(text):
    """
    Detect the language of the input text
    Returns 'hi' for Hindi or 'en' for English
    """
    try:
        lang = detect(text)
        return 'hi' if lang == 'hi' else 'en'
    except Exception as e:
        logger.error(f"Error detecting language: {str(e)}")
        return 'en'  # Default to English on error

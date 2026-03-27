"""Language codes, model identifiers, and platform constants."""

from __future__ import annotations

# ── Sarvam AI API Endpoints ────────────────────────────────────────
BASE_URL = "https://api.sarvam.ai"
CHAT_COMPLETIONS_URL = f"{BASE_URL}/v1/chat/completions"
STT_URL = f"{BASE_URL}/speech-to-text"
TTS_URL = f"{BASE_URL}/text-to-speech"
TRANSLATE_URL = f"{BASE_URL}/translate"
TRANSLITERATE_URL = f"{BASE_URL}/v1/transliterate"
LANGUAGE_ID_URL = f"{BASE_URL}/text-lid"

# ── Models ─────────────────────────────────────────────────────────
CHAT_MODEL = "sarvam-m"
STT_MODEL = "saarika:v2.5"
STT_BATCH_MODEL = "saaras:v2.5"
TTS_MODEL = "bulbul:v2"
TRANSLATE_MODEL = "mayura:v1"

# ── Defaults ───────────────────────────────────────────────────────
DEFAULT_TTS_SPEAKER = "meera"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# ── Supported Languages ───────────────────────────────────────────
SUPPORTED_LANGUAGES: dict[str, str] = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "bn-IN": "Bengali",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
}

LANGUAGE_DISPLAY_NAMES: dict[str, str] = {
    code: name for code, name in SUPPORTED_LANGUAGES.items()
}

LANGUAGE_SCRIPTS: dict[str, str] = {
    "hi-IN": "Devanagari",
    "bn-IN": "Bengali",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Devanagari",
    "gu-IN": "Gujarati",
    "pa-IN": "Gurmukhi",
    "od-IN": "Odia",
    "en-IN": "Latin",
}

# ── Limits ─────────────────────────────────────────────────────────
MAX_TTS_CHARS = 500
MAX_TRANSLATE_CHARS = 1000
MAX_CHAT_HISTORY_TURNS = 20
SUPPORTED_AUDIO_FORMATS = {"wav", "mp3", "aac", "ogg", "flac", "m4a"}

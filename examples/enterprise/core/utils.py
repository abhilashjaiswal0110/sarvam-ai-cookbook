"""Text-processing utilities: chunking, audio helpers."""

from __future__ import annotations

import base64


def chunk_text(text: str, max_length: int = 1000) -> list[str]:
    """Split text into chunks at sentence/word boundaries.

    Sarvam Translate API recommends ≤1000 chars per request;
    TTS API accepts ≤500 chars per call.
    """
    chunks: list[str] = []
    remaining = text.strip()
    while len(remaining) > max_length:
        # Prefer splitting at sentence boundary
        split_at = remaining.rfind(". ", 0, max_length)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length
        else:
            split_at += 1  # include the period/space
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def decode_audio_base64(b64_string: str) -> bytes:
    """Decode a base64-encoded audio string to bytes."""
    return base64.b64decode(b64_string)


def encode_audio_base64(audio_bytes: bytes) -> str:
    """Encode raw audio bytes to base64 string."""
    return base64.b64encode(audio_bytes).decode("ascii")

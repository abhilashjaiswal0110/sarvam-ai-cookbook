"""Tests for core utilities."""

from __future__ import annotations

from core.utils import chunk_text, decode_audio_base64, encode_audio_base64


class TestChunkText:
    def test_short_text_single_chunk(self) -> None:
        chunks = chunk_text("Hello world", 100)
        assert chunks == ["Hello world"]

    def test_splits_at_sentence_boundary(self) -> None:
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunk_text(text, 30)
        assert len(chunks) >= 2
        assert all(c.strip() for c in chunks)

    def test_splits_at_word_boundary(self) -> None:
        text = "word " * 50  # 250 chars
        chunks = chunk_text(text, 100)
        assert all(len(c) <= 105 for c in chunks)  # small overhead

    def test_empty_text(self) -> None:
        assert chunk_text("", 100) == []


class TestAudioBase64:
    def test_roundtrip(self) -> None:
        original = b"\x00\x01\x02\xff"
        encoded = encode_audio_base64(original)
        decoded = decode_audio_base64(encoded)
        assert decoded == original

from __future__ import annotations

from copyright_guard.similarity import similarity


def test_identical_texts_high_similarity():
    a = "the quick brown fox jumps over the lazy dog"
    assert similarity(a, a) == 1.0


def test_unrelated_texts_low_similarity():
    a = "the quick brown fox jumps over the lazy dog"
    b = "completely different content about a mountain range"
    assert similarity(a, b) < 0.2

from __future__ import annotations


def test_adapters_importable():
    import platforms.instagram.adapter  # noqa: F401
    import platforms.facebook.adapter  # noqa: F401
    import platforms.snapchat.adapter  # noqa: F401
    import platforms.twitter.adapter   # noqa: F401
    import platforms.telegram.adapter  # noqa: F401

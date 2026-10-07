from __future__ import annotations


def test_strategy_imports():
    from strategies.base_strategy import BaseStrategy  # noqa: F401
    from strategies.content_posting import ContentPostingStrategy  # noqa: F401
    from strategies.auto_reply import AutoReplyStrategy  # noqa: F401
    from strategies.cross_post import CrossPostStrategy  # noqa: F401

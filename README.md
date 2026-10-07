# techgeo

Multi-account social media bot for Instagram, Facebook, Snapchat, Twitter/X, and Telegram.

## Features
- Per-account isolation (fingerprint + proxy + cookies)
- Anti-detection layer (humanizer, rate limiter, circuit breaker)
- Copyright guard (input + output checks)
- Cross-platform posting via a single adapter interface
- Pluggable AI content generation

## Requirements
- Python 3.11+
- Redis 7+
- PostgreSQL 14+ (or SQLite for dev)
- Node.js 18+ (for Playwright browser automation)

## Quick Start
    cp .env.example .env
    pip install -r requirements.txt
    python scripts/seed_db.py
    python scripts/login_all.py
    python main.py

## License
Proprietary — internal use only.

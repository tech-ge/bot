# techgeo — First Run

## 1. Install
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium

## 2. Configure
    cp .env.example .env
    # edit .env: add tokens for the platforms you actually use

## 3. Init DB
    python scripts/seed_db.py

## 4. Sanity checks
    python -c "from config.settings import settings; print(settings.env)"
    python -c "from core.bot import BotManager; print('ok')"
    python -m compileall -q core platforms anti_detection copyright_guard \
        content ai strategies data analytics workers webhooks utils

## 5. Run tests
    pytest -q

## 6. Boot
    python main.py

## Notes
- Only configure accounts whose credentials you actually have.
  Empty tokens cause login() to warn and skip.
- Proxies are optional. Leave proxy `url: ""` to run direct.
- Snapchat organic posting is disabled; Marketing API only.
- Telegram bots need `chat_id` set in their YAML to post.

## Content sourcing (AI + web scraping)

Content priority order in `ContentPostingStrategy`:

1. **RSS feeds** — configured per account under `feeds:`
2. **Web URLs** — configured per account under `source_urls:`
3. **Topics only** — AI writes fresh if no sources or sources fail

The LLM rewrites scraped text so the output is unique (helps with copyright).

### Config example (account YAML)

    topics:
      - tech news
    feeds:
      - https://feeds.arstechnica.com/arstechnica/index
    source_urls:
      - https://news.ycombinator.com/

### Manual test

    python - <<'PY'
    import asyncio
    from content.sources.web_scraper import web_scraper

    async def main():
        p = await web_scraper.fetch("https://example.com")
        print(p.ok, p.title[:80], len(p.text))

    asyncio.run(main())
    PY

### Notes
- `trafilatura` extracts clean article text; `BeautifulSoup` is fallback.
- `feedparser` handles RSS/Atom.
- All fetched text passes through the LLM, then through `copyright_guard.output_checker`
  before posting.
- If no LLM key is set, the extractive `ai.summarizer` is used instead (no API call).

## Images

Three ways to attach images to posts (all funnel through `content/images/pipeline.py`):

1. **Local files** — set `images:` in account YAML
2. **Remote URLs** — set `image_urls:` in account YAML
3. **AI generation** — set `ai_image_prompt:` in account YAML (needs OPENAI_API_KEY)

Every image is:
- fetched or generated,
- checked against `copyright_guard`,
- resized/cropped to the platform's aspect ratio,
- optionally watermarked (`watermark:` in YAML),
- compressed under `max_size_kb` (default 1000).

### Post-editor quick test

    python - <<'PY'
    from content.images.editor.post_editor import PostEditor, EditOptions
    editor = PostEditor()
    # edit any local image for Instagram + add a watermark
    # out = editor.edit("path/to/img.jpg",
    #     EditOptions(aspect="instagram_square", watermark_text="@techgeo"))
    # print(out)
    PY

### Supported aspect presets
- `instagram_square`, `instagram_portrait`, `instagram_story`
- `facebook_feed`, `facebook_square`
- `twitter_landscape`, `twitter_square`
- `snapchat_story`
- `telegram`
- `generic`

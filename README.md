# Video Release Gate

> **Status (2026-09-18):** Thin extract only. **Do not treat as a separate product.** Fold into [`claude-video-kit`](https://github.com/runesleo/claude-video-kit) as the post-render publish gate. Prefer that repo for installs and issues.

Fail-closed release gate for agent-produced videos.

**Chinese:** [README.zh.md](./README.zh.md)

Prose QA is not a release gate. This CLI binds the final MP4, cover, three QA docs, and an independent final review to the same hashes — then machine-checks loudness, silence windows, and platform cover size before upload/schedule/publish.

## What you get

- `video_release_gate.py` — evaluate / verify CLI (`video_release_gate.v1`)
- `video_quality_profile.json` — quality ratchet (motion / composition / pacing floors)
- Unit tests that reproduce a real bad-master failure shape (too quiet / high LRA / self-approved review)

## How it works

1. Producer finishes the final video.
2. QA docs must embed the final video SHA256.
3. An independent reviewer (not the producer) writes `video_final_review.v1`.
4. Gate evaluates audio metrics + cover dimensions + hash bindings.
5. Publisher calls `verify` again immediately before upload; any asset/QA/review drift fails closed.

Exit codes: `0` PASS · `2` gate FAIL · `64` usage/config error.

## Quick start

```bash
python3 -m unittest discover -s tests -v

python3 video_release_gate.py evaluate \
  --video /path/to/final.mp4 \
  --cover /path/to/cover.png \
  --platform bilibili \
  --qa FACT-CHECK.md AUDIO-QA.md RENDER-QA.md \
  --review FINAL-REVIEW-bilibili.json \
  --out VIDEO-RELEASE-GATE-bilibili.json

python3 video_release_gate.py verify \
  --receipt VIDEO-RELEASE-GATE-bilibili.json \
  --video /path/to/final.mp4 \
  --platform bilibili \
  --cover /path/to/cover.png
```

Or: `./bin/video-release-gate …`

## Requirements

- Python 3.10+
- `ffprobe` on PATH
- Independent reviewer identity ≠ producer identity

## Privacy

No accounts, cookies, platform uploaders, or private media. Default project root: `./content/video`.

## Verified

- Local unit suite: 8/8 PASS
- Designed after a live publish incident where prose QA passed a bad master

## Known limitations

- Does not replace platform uploaders
- Cover presets: bilibili / YouTube / Xiaohongshu / WeChat Channels / X
- Motion quality still depends on human review scores + required profile checks

## Roadmap

- Optional adapters for common agent video kits
- More platform cover presets
- JSON Schema export for CI

## About the author

Built by [Leo](https://x.com/runes_leo) · [leolabs.me](https://leolabs.me/?utm_source=github&utm_medium=readme&utm_campaign=oss&utm_content=video-release-gate)

## License

MIT

# Video Release Gate — historical extract

**Canonical implementation: [claude-video-kit](https://github.com/runesleo/claude-video-kit).**

[中文](./README.zh.md)

This repository is a thin archive of the original final-video release gate.
It is not a separate product or installation target. Use, cite, and open issues
against `claude-video-kit`; ongoing implementation and tests live there.

- [Final gate guide: evaluate → verify → handoff](https://github.com/runesleo/claude-video-kit/blob/main/docs/RELEASE_GATE.md)
- [Canonical evaluate/verify CLI](https://github.com/runesleo/claude-video-kit/blob/main/scripts/video_release_gate.py)
- [Quality profile](https://github.com/runesleo/claude-video-kit/blob/main/config/video_quality_profile.json)
- [Regression tests](https://github.com/runesleo/claude-video-kit/blob/main/tests/test_video_release_gate.py)

The source and tests here remain only for historical reference. They do not
receive parallel feature development and should not be used as the current
publication gate. The canonical pipeline keeps its pre-render review and
`verify-shorts`, then checks the exact final MP4, cover, QA, independent final
review, audio measurements, and quality profile before distribution handoff.
Downstream uploaders must verify again immediately before any authorized action.
Neither implementation adds automatic upload or publication.

Migration context: [claude-video-kit #27](https://github.com/runesleo/claude-video-kit/issues/27).

MIT; see [LICENSE](./LICENSE).

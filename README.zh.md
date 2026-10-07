# Video Release Gate — 历史提取版

**唯一 canonical 实现：[claude-video-kit](https://github.com/runesleo/claude-video-kit)。**

[English](./README.md)

本仓库仅保留原始最终成片放行检查的代码与测试，作为 thin archive。
不再作为独立产品或安装入口，也不并行开发。使用、引用和提 issue 请统一指向主视频管线。

- [完整流程：evaluate → verify → 交付](https://github.com/runesleo/claude-video-kit/blob/main/docs/RELEASE_GATE.md)
- [canonical CLI](https://github.com/runesleo/claude-video-kit/blob/main/scripts/video_release_gate.py)
- [质量配置](https://github.com/runesleo/claude-video-kit/blob/main/config/video_quality_profile.json)
- [回归测试](https://github.com/runesleo/claude-video-kit/blob/main/tests/test_video_release_gate.py)

主管线保留渲染前审阅与 `verify-shorts`，并在分发交付前检查最终 MP4、封面、
三份 QA、独立终审、音频测量及质量配置的绑定关系。下游实际上传或排期前必须立即复验。
这里的历史代码不能代替 canonical gate；两者都不提供自动上传或发布。

迁移背景：[claude-video-kit #27](https://github.com/runesleo/claude-video-kit/issues/27)。

MIT，见 [LICENSE](./LICENSE)。

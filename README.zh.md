# Video Release Gate

> **状态（2026-09-18）**：仅作薄提取。**不要当独立产品推。** 应并入 [`claude-video-kit`](https://github.com/runesleo/claude-video-kit) 作为成片发布门。安装与 issue 请走 video-kit。

面向 Agent 产出视频的 fail-closed 发布门。

**English:** [README.md](./README.md)

散文式 QA 不等于发布门。这个 CLI 把最终 MP4、封面、三份 QA、独立终审绑定到同一组 hash，再机器核验响度、近静音窗口和平台封面尺寸；上传/排期/公开发布前必须再 `verify`。

## 你能得到什么

- `video_release_gate.py`：evaluate / verify CLI（`video_release_gate.v1`）
- `video_quality_profile.json`：质量棘轮
- 单元测试复现真实坏母带形态（过静 / 高 LRA / 生产者自审）

## 快速开始

```bash
python3 -m unittest discover -s tests -v
./bin/video-release-gate evaluate --help
```

## 要求

- Python 3.10+ · `ffprobe` · 独立审片人 ≠ 生产者

## 隐私

不含账号、cookies、uploader 或私有成片。默认项目根：`./content/video`。

## 已验证

本地单测 8/8 PASS。来自真实发布事故：散文 QA 放过了坏母带。

## License

MIT · [Leo](https://x.com/runes_leo) · [leolabs.me](https://leolabs.me/?utm_source=github&utm_medium=readme&utm_campaign=oss&utm_content=video-release-gate)

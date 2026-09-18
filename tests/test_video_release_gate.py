import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "video_release_gate.py"
SPEC = importlib.util.spec_from_file_location("video_release_gate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class VideoReleaseGateTests(unittest.TestCase):
    def _fixture(self, root: Path):
        canonical = root / "content" / "video"
        project = canonical / "2026-09-07-demo-999"
        out = project / "out"
        out.mkdir(parents=True)
        video = out / "final.mp4"
        video.write_bytes(b"video-v1")
        cover = project / "cover.png"
        cover.write_bytes(b"cover-v1")
        vsha = MODULE.sha256_file(video)
        csha = MODULE.sha256_file(cover)
        qas = []
        for name in ("FACT-CHECK-v1.md", "AUDIO-QA-v1.md", "RENDER-QA-v1.md"):
            path = project / name
            path.write_text(f"final_video_sha256: {vsha}\n", encoding="utf-8")
            qas.append(path)
        review = project / "FINAL-REVIEW-bilibili.json"
        profile = MODULE.load_quality_profile()
        checks = {name: True for name in MODULE.COMMON_REVIEW_CHECKS}
        checks.update({name: True for name in profile["required_review_checks"]})
        checks["bilibili_title_centered"] = True
        review.write_text(
            json.dumps(
                {
                    "schema": MODULE.REVIEW_SCHEMA,
                    "status": "PASS",
                    "platform": "bilibili",
                    "video_sha256": vsha,
                    "cover_sha256": csha,
                    "producer_id": "producer-session",
                    "reviewer_id": "reviewer-session",
                    "reviewed_at": "2026-09-07T12:00:00Z",
                    "quality_profile_version": profile["version"],
                    "quality_scores": {name: 5 for name in profile["minimum_scores"]},
                    "checks": checks,
                }
            ),
            encoding="utf-8",
        )
        return canonical, project, video, cover, qas, review

    def test_independent_reviewer_cannot_equal_producer(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            data = json.loads(review.read_text())
            data["reviewer_id"] = data["producer_id"]
            errors = MODULE.validate_review_receipt(
                data,
                platform="bilibili",
                video_sha=MODULE.sha256_file(video),
                cover_sha=MODULE.sha256_file(cover),
            )
            self.assertIn("producer cannot approve their own final asset", errors)

    def test_review_fails_below_current_motion_quality_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            data = json.loads(review.read_text())
            data["quality_scores"]["motion_design"] = 3
            errors = MODULE.validate_review_receipt(
                data,
                platform="bilibili",
                video_sha=MODULE.sha256_file(video),
                cover_sha=MODULE.sha256_file(cover),
            )
            self.assertTrue(any("motion_design=3" in e for e in errors))

    def test_review_fails_when_motion_v2_check_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            data = json.loads(review.read_text())
            data["checks"]["no_random_particles_or_floating_dots"] = False
            errors = MODULE.validate_review_receipt(
                data,
                platform="bilibili",
                video_sha=MODULE.sha256_file(video),
                cover_sha=MODULE.sha256_file(cover),
            )
            self.assertIn(
                "independent review check not PASS: no_random_particles_or_floating_dots",
                errors,
            )

    def test_audio_metrics_fail_quiet_high_lra_shape(self):
        metrics = {"integrated_lufs": -21.0, "lra_lu": 18.1, "true_peak_dbtp": -6.0}
        windows = [
            {"mean_db": -22.3, "silence_ratio": 0.04},
            {"mean_db": -38.3, "silence_ratio": 0.39},
            {"mean_db": -23.0, "silence_ratio": 0.10},
        ]
        errors = MODULE._audio_failures(metrics, windows)
        self.assertTrue(any("integrated loudness" in e for e in errors))
        self.assertTrue(any("LRA" in e for e in errors))
        self.assertTrue(any("mean level spread" in e for e in errors))

    def test_evaluate_pass_requires_hash_bound_qa_and_independent_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            video_probe = {
                "duration_s": 60.0,
                "width": 1920,
                "height": 1080,
                "audio_sample_rate": 48000,
                "audio_channels": 2,
                "has_video": True,
                "has_audio": True,
            }
            cover_probe = {
                "duration_s": 0.0,
                "width": 1920,
                "height": 1080,
                "audio_sample_rate": 0,
                "audio_channels": 0,
                "has_video": True,
                "has_audio": False,
            }
            with patch.object(MODULE, "probe_media", side_effect=[video_probe, cover_probe]):
                result = MODULE.evaluate_release(
                    project_dir=project,
                    video=video,
                    platform="bilibili",
                    cover=cover,
                    fact_qa=qas[0],
                    audio_qa=qas[1],
                    render_qa=qas[2],
                    review_receipt_path=review,
                    canonical_root=canonical,
                    measure_audio=False,
                    audio_metrics={"integrated_lufs": -14.0, "lra_lu": 5.0, "true_peak_dbtp": -2.0},
                    window_metrics=[
                        {"mean_db": -24.0, "silence_ratio": 0.10},
                        {"mean_db": -22.0, "silence_ratio": 0.12},
                        {"mean_db": -23.0, "silence_ratio": 0.08},
                    ],
                )
            self.assertEqual(result["status"], "PASS", result["failures"])

    def test_evaluate_fails_when_qa_does_not_bind_final_video_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            qas[1].write_text("audio: PASS\n", encoding="utf-8")
            video_probe = {
                "duration_s": 60.0,
                "width": 1920,
                "height": 1080,
                "audio_sample_rate": 48000,
                "audio_channels": 2,
                "has_video": True,
                "has_audio": True,
            }
            cover_probe = {
                "duration_s": 0.0,
                "width": 1920,
                "height": 1080,
                "audio_sample_rate": 0,
                "audio_channels": 0,
                "has_video": True,
                "has_audio": False,
            }
            with patch.object(MODULE, "probe_media", side_effect=[video_probe, cover_probe]):
                result = MODULE.evaluate_release(
                    project_dir=project,
                    video=video,
                    platform="bilibili",
                    cover=cover,
                    fact_qa=qas[0],
                    audio_qa=qas[1],
                    render_qa=qas[2],
                    review_receipt_path=review,
                    canonical_root=canonical,
                    measure_audio=False,
                    audio_metrics={"integrated_lufs": -14.0, "lra_lu": 5.0, "true_peak_dbtp": -2.0},
                    window_metrics=[
                        {"mean_db": -24.0, "silence_ratio": 0.10},
                        {"mean_db": -22.0, "silence_ratio": 0.12},
                        {"mean_db": -23.0, "silence_ratio": 0.08},
                    ],
                )
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("AUDIO QA does not contain" in e for e in result["failures"]))

    def test_verify_rejects_stale_pass_after_video_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            receipt = project / "VIDEO-RELEASE-GATE-bilibili.json"
            profile = MODULE.load_quality_profile()
            payload = {
                "schema": MODULE.SCHEMA,
                "status": "PASS",
                "platform": "bilibili",
                "quality_profile": {
                    "schema": profile["schema"],
                    "version": profile["version"],
                    "sha256": profile["_sha256"],
                    "path": profile["_path"],
                },
                "video": {"sha256": MODULE.sha256_file(video)},
                "cover": {"sha256": MODULE.sha256_file(cover)},
                "qa": {
                    "fact": {"path": str(qas[0]), "sha256": MODULE.sha256_file(qas[0])},
                    "audio": {"path": str(qas[1]), "sha256": MODULE.sha256_file(qas[1])},
                    "render": {"path": str(qas[2]), "sha256": MODULE.sha256_file(qas[2])},
                },
                "independent_review": {"path": str(review), "sha256": MODULE.sha256_file(review)},
            }
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            video.write_bytes(b"video-v2")
            errors = MODULE.verify_pass_receipt(receipt, video, "bilibili", cover)
            self.assertIn("final video changed after release gate PASS", errors)

    def test_verify_rejects_old_quality_profile_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            canonical, project, video, cover, qas, review = self._fixture(Path(tmp))
            receipt = project / "VIDEO-RELEASE-GATE-bilibili.json"
            profile = MODULE.load_quality_profile()
            payload = {
                "schema": MODULE.SCHEMA,
                "status": "PASS",
                "platform": "bilibili",
                "quality_profile": {
                    "schema": profile["schema"],
                    "version": "older-motion-profile",
                    "sha256": "stale",
                    "path": profile["_path"],
                },
                "video": {"sha256": MODULE.sha256_file(video)},
                "cover": {"sha256": MODULE.sha256_file(cover)},
                "qa": {
                    "fact": {"path": str(qas[0]), "sha256": MODULE.sha256_file(qas[0])},
                    "audio": {"path": str(qas[1]), "sha256": MODULE.sha256_file(qas[1])},
                    "render": {"path": str(qas[2]), "sha256": MODULE.sha256_file(qas[2])},
                },
                "independent_review": {"path": str(review), "sha256": MODULE.sha256_file(review)},
            }
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            errors = MODULE.verify_pass_receipt(receipt, video, "bilibili", cover)
            self.assertIn("video quality profile changed after release gate PASS; re-review required", errors)


if __name__ == "__main__":
    unittest.main()

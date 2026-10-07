from __future__ import annotations

from anti_detection.fingerprint import FingerprintManager


def test_generate_and_persist(tmp_path):
    mgr = FingerprintManager(base_dir=tmp_path)
    fp = mgr.load_or_create("acc_01")
    assert fp.profile_id == "acc_01"
    fp2 = mgr.load_or_create("acc_01")
    assert fp.user_agent == fp2.user_agent
    ctx = mgr.browser_context_args(fp)
    assert "user_agent" in ctx

"""Frozen releases must pass the same independent gate as candidate inputs."""

from types import SimpleNamespace
import json
import subprocess

import pytest

from baseline import releases


def test_release_validation_cannot_bypass_dataset_gate(tmp_path, monkeypatch):
    manifest = tmp_path / "dataset/manifest.json"
    manifest.parent.mkdir()
    manifest.write_text('{"tasks":[]}')
    descriptor = {
        "dataset_manifest": "dataset/manifest.json",
        "dataset_git_commit": "a" * 40,
        "evaluation_protocol_fingerprint": releases.evaluation_protocol_fingerprint(),
        "expected_task_count": 1,
        "dataset_fingerprint": "b" * 64,
    }
    monkeypatch.setattr(releases.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout=manifest.read_bytes()))
    monkeypatch.setattr("baseline.runner.dataset_fingerprint", lambda items: "b" * 64)
    checked = []

    def reject(path):
        checked.append(path)
        raise ValueError("Independent pixel gate rejected the corpus")

    monkeypatch.setattr("baseline.validate_dataset.require_valid_dataset", reject)
    with pytest.raises(ValueError, match="Independent pixel gate"):
        releases.validate_release(descriptor, root=tmp_path, items=[{}])
    assert checked == [manifest]


@pytest.mark.parametrize("mutation", ["catalog", "license", "extra"])
def test_supplemental_artifacts_are_bound_to_the_dataset_commit(tmp_path, monkeypatch, mutation):
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, text=True, capture_output=True, check=True).stdout.strip()

    git("init", "-q")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Fixture")
    dataset = tmp_path / "dataset/frozen"
    dataset.mkdir(parents=True)
    manifest = dataset / "manifest.json"
    manifest.write_text('{"tasks":[]}')
    (dataset / "catalog.json").write_text("{}")
    (dataset / "LICENSE").write_text("frozen license")
    git("add", ".")
    git("commit", "-qm", "Frozen dataset fixture")
    descriptor = {
        "dataset_manifest": "dataset/frozen/manifest.json",
        "dataset_git_commit": git("rev-parse", "HEAD"),
        "evaluation_protocol_fingerprint": releases.evaluation_protocol_fingerprint(),
        "expected_task_count": 1,
        "dataset_fingerprint": "b" * 64,
    }
    monkeypatch.setattr("baseline.runner.dataset_fingerprint", lambda items: "b" * 64)
    monkeypatch.setattr("baseline.validate_dataset.require_valid_dataset", lambda path: {})
    assert releases.validate_release(descriptor, root=tmp_path, items=[{}]) == [{}]
    if mutation == "catalog":
        (dataset / "catalog.json").write_text(json.dumps({"changed": True}))
    elif mutation == "license":
        (dataset / "LICENSE").write_text("changed license")
    else:
        (dataset / "unregistered.png").write_text("unregistered bytes")
    with pytest.raises(ValueError, match="[Dd]ataset artifact"):
        releases.validate_release(descriptor, root=tmp_path, items=[{}])

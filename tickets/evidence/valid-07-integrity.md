# Integrity regression evidence

Base: `077578b121561fb657cb7fc58fd1940b9a0e7b57`. Temporary fixtures only; released assets remain untouched.

## Red evidence

### python

```text
FFFFFFFFFF                                                               [100%]
=================================== FAILURES ===================================
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>0] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide0')
mutation = <function <lambda> at 0x7fe0a6173b00>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>1] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide1')
mutation = <function <lambda> at 0x7fe0a6173ba0>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>2] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide2')
mutation = <function <lambda> at 0x7fe0a6173c40>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
>       report = validate_dataset(manifest, min_per_label=1)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_validate_dataset.py:210: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
baseline/validate_dataset.py:295: in validate_dataset
    _check_evidence(item, fail)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

item = {'taskId': 't1', 'imageFilename': 't1.png', 'imagePath': 't1.png', 'groundTruth': {'has_border': True, 'border_sides': 'all-4', 'stroke_style': 'solid', 'stroke_width': '1px', ...}, ...}
fail = <function validate_dataset.<locals>.fail at 0x7fe0a5d11c60>

    def _check_evidence(item: dict, fail) -> None:
        task_id = item.get("taskId")
        gt = item.get("groundTruth", {})
        rendered = item.get("rendered")
        if not isinstance(rendered, dict):
            fail("evidence_shape", "Missing rendered evidence object", task_id)
            return
        if not isinstance(rendered.get("browser"), str) or not rendered["browser"].strip():
            fail("evidence_shape", "Rendered evidence must record the browser version", task_id)
        card = rendered.get("card")
        if not isinstance(card, dict):
            fail("evidence_shape", "Rendered evidence must record the card box", task_id)
            return
        try:
            for key in ("x", "y", "width", "height"):
>               if abs(float(card[key]) - CARD_CSS[key]) > 2:
                             ^^^^^^^^^
E               KeyError: 'x'

baseline/validate_dataset.py:107: KeyError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>3] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide3')
mutation = <function <lambda> at 0x7fe0a6173ce0>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
>       report = validate_dataset(manifest, min_per_label=1)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_validate_dataset.py:210: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
baseline/validate_dataset.py:295: in validate_dataset
    _check_evidence(item, fail)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

item = {'taskId': 't1', 'imageFilename': 't1.png', 'imagePath': 't1.png', 'groundTruth': 'broken', ...}
fail = <function validate_dataset.<locals>.fail at 0x7fe0a5d12840>

    def _check_evidence(item: dict, fail) -> None:
        task_id = item.get("taskId")
        gt = item.get("groundTruth", {})
        rendered = item.get("rendered")
        if not isinstance(rendered, dict):
            fail("evidence_shape", "Missing rendered evidence object", task_id)
            return
        if not isinstance(rendered.get("browser"), str) or not rendered["browser"].strip():
            fail("evidence_shape", "Rendered evidence must record the browser version", task_id)
        card = rendered.get("card")
        if not isinstance(card, dict):
            fail("evidence_shape", "Rendered evidence must record the card box", task_id)
            return
        try:
            for key in ("x", "y", "width", "height"):
                if abs(float(card[key]) - CARD_CSS[key]) > 2:
                    fail("evidence_geometry", f"Card {key} {card[key]} differs from canonical {CARD_CSS[key]}", task_id)
        except (TypeError, ValueError):
            fail("evidence_shape", "Card box must hold finite numbers", task_id)
            return
        computed = rendered.get("computed")
        if not isinstance(computed, dict):
            fail("evidence_shape", "Rendered evidence must record computed styles", task_id)
            return
>       width_px = WIDTH_PX.get(gt.get("stroke_width"), None)
                                ^^^^^^
E       AttributeError: 'str' object has no attribute 'get'

baseline/validate_dataset.py:116: AttributeError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>4] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide4')
mutation = <function <lambda> at 0x7fe0a6173d80>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>5] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide5')
mutation = <function <lambda> at 0x7fe0a6173e20>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>6] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide6')
mutation = <function <lambda> at 0x7fe0a6173ec0>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
__________ test_malformed_or_forged_evidence_fails_closed[<lambda>7] ___________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_malformed_or_forged_evide7')
mutation = <function <lambda> at 0x7fe0a6173f60>

    @pytest.mark.parametrize("mutation", [
        lambda row: row["rendered"]["card"].update(x=float("nan")),
        lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
        lambda row: row["rendered"]["card"].pop("x"),
        lambda row: row.update(groundTruth="broken"),
        lambda row: row["groundTruth"].update(has_border=1),
        lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
        lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
    ])
    def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        mutation(data["tasks"][0])
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert not report["valid"], "Malformed evidence must fail with findings, without crashing"
E       AssertionError: Malformed evidence must fail with findings, without crashing
E       assert not True

tests/test_validate_dataset.py:211: AssertionError
________________ test_incorrect_declared_task_count_is_rejected ________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_incorrect_declared_task_c0')

    def test_incorrect_declared_task_count_is_rejected(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        data["total_tasks"] = 999
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1)
>       assert any(error["code"] == "manifest_count" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_incorrect_declared_task_count_is_rejected.<locals>.<genexpr> at 0x7fe0a60a5700>)

tests/test_validate_dataset.py:220: AssertionError
____________________ test_release_gate_requires_every_label ____________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-182/test_release_gate_requires_eve0')

    def test_release_gate_requires_every_label(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        report = validate_dataset(manifest)
>       assert any(error["code"] == "coverage" for error in report["errors"]), "Absent classes need explicit coverage findings"
E       AssertionError: Absent classes need explicit coverage findings
E       assert False
E        +  where False = any(<generator object test_release_gate_requires_every_label.<locals>.<genexpr> at 0x7fe0a5dbcc70>)

tests/test_validate_dataset.py:226: AssertionError
=========================== short test summary info ============================
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>0]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>1]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>2]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>3]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>4]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>5]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>6]
FAILED tests/test_validate_dataset.py::test_malformed_or_forged_evidence_fails_closed[<lambda>7]
FAILED tests/test_validate_dataset.py::test_incorrect_declared_task_count_is_rejected
FAILED tests/test_validate_dataset.py::test_release_gate_requires_every_label
10 failed, 10 deselected in 1.33s
```

### ts

```text
bun test v1.3.14 (0d9b296a)

src/render-protection.test.ts:
(pass) render protection > refuses historical and registered release directories [1.64ms]
(pass) render protection > allows candidate and unregistered directories [0.06ms]
24 |     const frozen = path.join(root, "frozen");
25 |     fs.mkdirSync(frozen);
26 |     fs.symlinkSync(frozen, path.join(root, "alias"));
27 |     fs.symlinkSync(path.join(frozen, "missing"), path.join(root, "dangling"));
28 |     for (const destination of [root, frozen, path.join(frozen, "child"), path.join(root, "alias"), path.join(root, "alias/new"), path.join(root, "dangling/child")]) {
29 |       expect(() => refuseProtectedDir(destination, [frozen])).toThrow();
                                                                   ^
error: expect(received).toThrow()

Received function did not throw
Received value: undefined

      at <anonymous> (/mnt/disks/data/borderbench/src/render-protection.test.ts:29:63)
(fail) refuses release ancestors, descendants, and symlink aliases [0.59ms]
43 |     for (const entry of ["{", "{}", '{"dataset_path":"../outside"}', '{"dataset_path":"dataset/frozen"}']) {
44 |       fs.writeFileSync(file, entry);
45 |       expect(() => renderer.releaseDatasetPaths(root)).toThrow();
46 |     }
47 |     fs.writeFileSync(file, JSON.stringify({ dataset_path: "dataset/frozen", dataset_manifest: "dataset/frozen/manifest.json" }));
48 |     expect(renderer.releaseDatasetPaths(root)).toEqual([path.join(root, "dataset/frozen")]);
                         ^
TypeError: renderer.releaseDatasetPaths is not a function. (In 'renderer.releaseDatasetPaths(root)', 'renderer.releaseDatasetPaths' is undefined)
      at <anonymous> (/mnt/disks/data/borderbench/src/render-protection.test.ts:48:21)
(fail) malformed or missing release registry fails closed [0.57ms]

 2 pass
 2 fail
 11 expect() calls
Ran 4 tests across 1 file. [263.00ms]
```

### preflight

```text
F                                                                        [100%]
=================================== FAILURES ===================================
______________ test_release_validation_cannot_bypass_dataset_gate ______________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-183/test_release_validation_cannot0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7f7a69f7a890>

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
>       with pytest.raises(ValueError, match="Independent pixel gate"):
E       Failed: DID NOT RAISE ValueError

tests/test_release_preflight.py:30: Failed
=========================== short test summary info ============================
FAILED tests/test_release_preflight.py::test_release_validation_cannot_bypass_dataset_gate
1 failed in 0.13s
```


### RGB PNG transparency Red

```text
F                                                                        [100%]
=================================== FAILURES ===================================
___________________ test_rgb_transparency_chunk_is_rejected ____________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-198/test_rgb_transparency_chunk_is0')

    def test_rgb_transparency_chunk_is_rejected(tmp_path):
        image = Image.open(io.BytesIO(_card_image())).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", transparency=(255, 255, 255))
        manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()})
        report = validate_dataset(manifest, min_per_label=1, require_complete=False)
>       assert any(error["code"] == "png_alpha" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_rgb_transparency_chunk_is_rejected.<locals>.<genexpr> at 0x7f07a527cee0>)

tests/test_validate_dataset.py:286: AssertionError
=========================== short test summary info ============================
FAILED tests/test_validate_dataset.py::test_rgb_transparency_chunk_is_rejected
1 failed, 24 deselected in 0.21s
```

### Shadow scale Red

```text
F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_shadow_pixels_must_match_the_coarse_spread_category ___________

    def test_shadow_pixels_must_match_the_coarse_spread_category():
        from baseline.validate_dataset import _check_pixels
    
        flat = Image.open(io.BytesIO(_card_image())).convert("RGB")
        image = flat.copy()
        ImageDraw.Draw(image).rectangle((200, 610, 919, 634), fill=(225, 229, 233))
        item = {"taskId": "t1", "groundTruth": {
            "has_border": True, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px",
            "corner_radius": "medium", "corner_radius_px": 12, "elevation": "subtle-drop", "theme": "white-on-gray",
        }}
        findings = []
        _check_pixels(item, image, flat, lambda code, *args: findings.append(code))
>       assert "pixel_shadow_scale" in findings
E       AssertionError: assert 'pixel_shadow_scale' in []

tests/test_validate_dataset.py:292: AssertionError
=========================== short test summary info ============================
FAILED tests/test_validate_dataset.py::test_shadow_pixels_must_match_the_coarse_spread_category
1 failed, 25 deselected in 0.18s
```

## Isolated reversion

Original validator/release functions from base commit were loaded into isolated Python namespaces; repository files remained unchanged. The same9 regression checks fail for missing coverage/count/pixel/alpha/preflight/artifact enforcement.

```text
FFFFFFFFF                                                                [100%]
=================================== FAILURES ===================================
________________ test_incorrect_declared_task_count_is_rejected ________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_incorrect_declared_task_c0')

    def test_incorrect_declared_task_count_is_rejected(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        data = json.loads(manifest.read_text())
        data["total_tasks"] = 999
        manifest.write_text(json.dumps(data))
        report = validate_dataset(manifest, min_per_label=1, require_complete=False)
>       assert any(error["code"] == "manifest_count" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_incorrect_declared_task_count_is_rejected.<locals>.<genexpr> at 0x7fe65b081a40>)

tests/test_validate_dataset.py:236: AssertionError
____________________ test_release_gate_requires_every_label ____________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_release_gate_requires_eve0')

    def test_release_gate_requires_every_label(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image()})
        report = validate_dataset(manifest)
>       assert any(error["code"] == "coverage" for error in report["errors"]), "Absent classes need explicit coverage findings"
E       AssertionError: Absent classes need explicit coverage findings
E       assert False
E        +  where False = any(<generator object test_release_gate_requires_every_label.<locals>.<genexpr> at 0x7fe65b082b50>)

tests/test_validate_dataset.py:242: AssertionError
______________ test_pixels_cannot_claim_a_different_border_width _______________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_pixels_cannot_claim_a_dif0')

    def test_pixels_cannot_claim_a_different_border_width(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image(8)})
        report = validate_dataset(manifest, min_per_label=1, require_complete=False)
>       assert any(error["code"] == "pixel_width" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_pixels_cannot_claim_a_different_border_width.<locals>.<genexpr> at 0x7fe65b083920>)

tests/test_validate_dataset.py:248: AssertionError
_________________ test_pixels_cannot_claim_a_different_radius __________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_pixels_cannot_claim_a_dif1')

    def test_pixels_cannot_claim_a_different_radius(tmp_path):
        manifest = _write_corpus(tmp_path, {"t1": _card_image(1, radius_px=24)})
        report = validate_dataset(manifest, min_per_label=1, require_complete=False)
>       assert any(error["code"] == "pixel_radius" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_pixels_cannot_claim_a_different_radius.<locals>.<genexpr> at 0x7fe65b082a80>)

tests/test_validate_dataset.py:254: AssertionError
___________________ test_rgb_transparency_chunk_is_rejected ____________________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_rgb_transparency_chunk_is0')

    def test_rgb_transparency_chunk_is_rejected(tmp_path):
        image = Image.open(io.BytesIO(_card_image())).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", transparency=(255, 255, 255))
        manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()})
        report = validate_dataset(manifest, min_per_label=1, require_complete=False)
>       assert any(error["code"] == "png_alpha" for error in report["errors"])
E       assert False
E        +  where False = any(<generator object test_rgb_transparency_chunk_is_rejected.<locals>.<genexpr> at 0x7fe659c8c040>)

tests/test_validate_dataset.py:318: AssertionError
______________ test_release_validation_cannot_bypass_dataset_gate ______________

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_release_validation_cannot0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fe659739790>

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
>       with pytest.raises(ValueError, match="Independent pixel gate"):
E       Failed: DID NOT RAISE ValueError

tests/test_release_preflight.py:32: Failed
_____ test_supplemental_artifacts_are_bound_to_the_dataset_commit[catalog] _____

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_supplemental_artifacts_ar0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fe659714850>
mutation = 'catalog'

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
>       with pytest.raises(ValueError, match="[Dd]ataset artifact"):
E       Failed: DID NOT RAISE ValueError

tests/test_release_preflight.py:69: Failed
_____ test_supplemental_artifacts_are_bound_to_the_dataset_commit[license] _____

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_supplemental_artifacts_ar1')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fe659750d10>
mutation = 'license'

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
>       with pytest.raises(ValueError, match="[Dd]ataset artifact"):
E       Failed: DID NOT RAISE ValueError

tests/test_release_preflight.py:69: Failed
______ test_supplemental_artifacts_are_bound_to_the_dataset_commit[extra] ______

tmp_path = PosixPath('/tmp/pytest-of-ted/pytest-220/test_supplemental_artifacts_ar2')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fe659c93850>
mutation = 'extra'

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
>       with pytest.raises(ValueError, match="[Dd]ataset artifact"):
E       Failed: DID NOT RAISE ValueError

tests/test_release_preflight.py:69: Failed
=========================== short test summary info ============================
FAILED tests/test_validate_dataset.py::test_incorrect_declared_task_count_is_rejected
FAILED tests/test_validate_dataset.py::test_release_gate_requires_every_label
FAILED tests/test_validate_dataset.py::test_pixels_cannot_claim_a_different_border_width
FAILED tests/test_validate_dataset.py::test_pixels_cannot_claim_a_different_radius
FAILED tests/test_validate_dataset.py::test_rgb_transparency_chunk_is_rejected
FAILED tests/test_release_preflight.py::test_release_validation_cannot_bypass_dataset_gate
FAILED tests/test_release_preflight.py::test_supplemental_artifacts_are_bound_to_the_dataset_commit[catalog]
FAILED tests/test_release_preflight.py::test_supplemental_artifacts_are_bound_to_the_dataset_commit[license]
FAILED tests/test_release_preflight.py::test_supplemental_artifacts_are_bound_to_the_dataset_commit[extra]
9 failed, 22 deselected in 0.57s
```

## Verification gates

Base: `077578b121561fb657cb7fc58fd1940b9a0e7b57`; candidate source checkout contains the working V1.2.0 changes.

| Gate | Outcome |
| --- | --- |
| `pytest tests/test_validate_dataset.py tests/test_release_preflight.py tests/test_frozen_ci.py -q` | 32 passed |
| `bun test src/render-protection.test.ts` | 4 passed; 18 assertions |
| Candidate all-image validation | 477 samples, 477 unique decoded images, one independently hashed font, zero findings |
| Candidate manifest SHA-256 | `0399662ed2091d71dd6ef66a60a7cd79f6abd9b336591db88110c8633c35bb78` |
| Isolated base-code reversion | 9 selected regression failures recur |
| `git diff --check` for integrity-owned files | Clean |

## Decisions and durable findings

- Canonical label validation is strict about JSON booleans, numeric finiteness, dependent no-border values, corner arrays, and exact frozen Tailwind CSS stacks.
- Dataset completeness binds every catalog task, prompt, reference font, PNG and recorded total. Full releases additionally bind the exact artifact set and bytes at the dataset Git commit, including catalog/font/license/validation files.
- Pixel probes measure all four actual side widths, broken versus solid strokes, dashed versus dotted segment lengths, all corner silhouettes, fixed reference text and scale-rule visibility. Coarse edge probes are calibrated to the frozen Chromium corpus; they do not claim arbitrary CSS reconstruction.
- Each elevated input names a hashed flat control from the same recipe and theme. Exterior pixel differences establish shadow observability; exterior extent separates retained subtle and floating buckets. None/subtle/floating occur for every recipe/theme.
- Frozen release validation now runs the independent gate before the runner can construct provider clients. Freezing image hashes without checking rendered evidence is insufficient.
- Generation resolves symlinks and refuses protected ancestors, descendants and historical paths. A malformed release registry fails closed. CI protects every release already registered in the comparison commit while allowing a new version directory/descriptor.
- FontBench parity audit also identified absent finalization, response re-scoring and shared-cohort guarantees; root/evaluation lanes own those changes. FontBench itself is a useful reference, not proof of validity.
- Simplification pass kept the perimeter/font/shadow checks in one validator with small algorithm-specific helpers; removed unused color binding and duplicate CLI validation. No framework or configurable validation language introduced.

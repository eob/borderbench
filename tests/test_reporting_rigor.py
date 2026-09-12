"""Release reports require auditable, correctly graded observation records."""
import json
from pathlib import Path

import pytest

from baseline.build_page import collect_observations
from baseline.reporting import scorecard_tasks
from test_release_runs import _release, _row, _write_run


def test_unsupported_and_inconsistent_rows_are_excluded(tmp_path):
    root = tmp_path / '9.9.9'
    root.mkdir()
    row = _row('foreign-task', True)
    row.update(raw_prediction='{}', stroke_width_correct=False)
    _write_run(root, 'bad', [row], 'not-a-date')
    collected, warnings = collect_observations(_release(), tmp_path)
    assert collected['observations'] == {}
    assert warnings


def test_inconsistent_exact_flag_rejected(tmp_path):
    root = tmp_path / '9.9.9'
    root.mkdir()
    row = _row('t1', True)
    row['stroke_width_correct'] = False
    _write_run(root, 'bad', [row], '2026-09-10T00:00:00+00:00')
    card = json.loads((root / 'bad' / 'scorecard_mock-model.json').read_text())
    with pytest.raises(ValueError, match='grading|exact|flags'):
        scorecard_tasks(card, dataset_fingerprint=_release()['dataset_fingerprint'])


def test_resumed_old_campaign_cannot_replace_an_earlier_final_answer(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    _write_run(root, 'old-campaign', [{**_row('t1', True), 'recorded_at': '2026-09-12T00:00:00+00:00'}], '2026-09-01T00:00:00+00:00')
    _write_run(root, 'first-answer', [_row('t1', False)], '2026-09-10T00:00:00+00:00')
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not warnings
    observation, = data['observations'].values()
    assert observation['run'] == 'first-answer'
    assert observation['task']['all_correct'] is False
    config, = data['configs'].values()
    assert config['repeat_observations'] == 1


@pytest.mark.parametrize('mutation', ['raw', 'target', 'config', 'foreign', 'missing-ledger', 'timestamp', 'negative-cost'])
def test_forged_records_fail_closed(tmp_path, mutation):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    _write_run(root, 'run', [_row('t1', True)], '2026-09-10T00:00:00+00:00')
    path = root / 'run' / 'scorecard_mock-model.json'
    card = json.loads(path.read_text())
    if mutation == 'raw': card['tasks'][0]['raw_prediction'] = '{}'
    if mutation == 'target': card['tasks'][0]['stroke_width_gt'] = '8px'
    if mutation == 'foreign': card['tasks'][0]['task_id'] = 'foreign'
    if mutation == 'config': card['model_config']['max_output_tokens'] = 32
    if mutation == 'timestamp': card['tasks'][0]['recorded_at'] = '2026-01-01T00:00:00+00:00'
    if mutation == 'negative-cost': card['tasks'][0]['cost_usd'] = -1
    path.write_text(json.dumps(card))
    if mutation == 'missing-ledger': (root / 'run' / 'attempts.jsonl').unlink()
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not data['observations']
    assert warnings


def test_raw_replay_rejects_consistently_forged_flags(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    row = _row('t1', False)
    for key in list(row):
        if key.endswith('_correct'): row[key] = True
    _write_run(root, 'forged', [row], '2026-09-10T00:00:00+00:00')
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not data['observations']
    assert any('raw prediction replay' in warning for warning in warnings)


def test_attempt_costs_include_retry_infrastructure_failures(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    _write_run(root, 'run', [_row('t1', True)], '2026-09-10T00:00:00+00:00')
    directory = root / 'run'
    ledger = directory / 'attempts.jsonl'
    success = json.loads(ledger.read_text()); success['sequence'] = 2
    error = {**success, 'sequence': 1, 'attempt_id': 'failed', 'cost_usd': .1,
             'result': {'task_id': 't1', 'error': 'timeout', 'error_kind': 'unavailable', 'cost_usd': .1}}
    ledger.write_text(json.dumps(error) + '\n' + json.dumps(success) + '\n')
    summary_path = directory / 'summary.json'
    summary = json.loads(summary_path.read_text())
    summary['spent_cost_usd'] = .11; summary['models']['mock-model']['cost_usd'] = .11
    summary_path.write_text(json.dumps(summary))
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not warnings
    config, = data['configs'].values()
    assert config['total_cost_usd'] == pytest.approx(.11)
    assert config['infrastructure_errors'] == 1


def test_page_uses_shared_scores_for_ranking_and_rendering(tmp_path, monkeypatch):
    import baseline.build_page as page
    from test_release_runs import _items, _tiny_png
    items = _items()
    for item in items:
        item['imageFilename'] = item['taskId'] + '.png'
        item['imagePath'] = str(tmp_path / item['imageFilename'])
        Path(item['imagePath']).write_bytes(_tiny_png())
    configs = {key: {'id': key, 'display_name': label, 'provider': 'google', 'runs': ['fixture']}
               for key, label in [('a', 'Zeta'), ('b', 'Alpha')]}
    collected = {'configs': configs, 'observations': {
        ('a', 't1'): {'task': _row('t1', True)},
        ('b', 't1'): {'task': _row('t1', True)}, ('b', 't2'): {'task': _row('t2', False)},
    }, 'runs': [], 'excluded_runs': [], 'duplicate_policy': 'first'}
    monkeypatch.setattr(page, 'load_release', lambda *a: _release())
    monkeypatch.setattr(page, 'release_manifest_path', lambda *a: tmp_path / 'manifest.json')
    monkeypatch.setattr(page, 'validate_release', lambda *a: items)
    monkeypatch.setattr(page, 'validate_dataset', lambda *a: {'valid': True, 'distributions': {}})
    monkeypatch.setattr(page, 'collect_observations', lambda *a: (collected, []))
    result = page.build_page('9.9.9', tmp_path, tmp_path / 'site', site_url='https://example.org/benchmarks/borders/')
    assert result['shared_task_ids'] == ['t1']
    assert [row['display_name'] for row in result['configs']] == ['Alpha', 'Zeta']
    assert [row['shared_metrics']['exact'] for row in result['configs']] == [1, 1]
    assert result['configs'][0]['metrics']['exact'] == .5
    html = (tmp_path / 'site/index.html').read_text()
    assert '50.0%' not in html
    from html.parser import HTMLParser
    class Metadata(HTMLParser):
        values = {}
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'meta':
                self.values[attrs.get('property', attrs.get('name'))] = attrs.get('content')
    metadata = Metadata()
    metadata.feed(html)
    assert metadata.values['twitter:card'] == 'summary_large_image'
    assert metadata.values['og:image'] == 'https://example.org/benchmarks/borders/assets/borderbench-share.png'
    assert metadata.values['twitter:image'] == metadata.values['og:image']
    assert metadata.values['og:image:width'] == '1200'
    assert metadata.values['og:image:height'] == '630'
    from PIL import Image
    with Image.open(tmp_path / 'site/assets/borderbench-share.png') as card:
        assert card.size == (1200, 630)
    assert (tmp_path / 'site/assets/borderbench-logo.svg').is_file()


def test_parseable_correct_answer_cannot_be_relabeled_invalid(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    row = _row('t1', True)
    row.update(error='claimed malformed', error_kind='invalid_response')
    for key in list(row):
        if key.endswith('_correct'): row[key] = False
    _write_run(root, 'forged', [row], '2026-09-10T00:00:00+00:00')
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not data['observations']
    assert any('parseable' in warning.lower() for warning in warnings)


def test_invalid_final_answer_remains_zero_after_later_correct_repeat(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    row = _row('t1', False)
    row.update(raw_prediction='{}', error='missing prediction keys', error_kind='invalid_response')
    _write_run(root, 'first-invalid', [row], '2026-09-10T00:00:00+00:00')
    _write_run(root, 'second-correct', [_row('t1', True)], '2026-09-11T00:00:00+00:00')
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not warnings
    observation, = data['observations'].values()
    config, = data['configs'].values()
    assert observation['task']['error_kind'] == 'invalid_response'
    assert observation['task']['all_correct'] is False
    assert config['total_cost_usd'] == pytest.approx(.02)
    assert config['repeat_cost_usd'] == pytest.approx(.01)


def test_unknown_latency_stays_an_unknown_measurement(tmp_path):
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    row = _row('t1', True); row['latency_sec'] = None
    _write_run(root, 'unknown-latency', [row], '2026-09-10T00:00:00+00:00')
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert not warnings
    observation, = data['observations'].values()
    assert observation['task']['latency_sec'] is None


@pytest.mark.parametrize('cost_adjustment,accepted', [(0.0, True), (0.000001, False)])
def test_ledger_cost_comparison_tolerates_only_float_roundoff(tmp_path, cost_adjustment, accepted):
    import math
    from test_release_runs import _items
    root = tmp_path / '9.9.9'; root.mkdir()
    rows = [_row('t1', True), _row('t2', True)]
    for row in rows:
        row['cost_usd'] = .0004
    _write_run(root, 'retry-costs', rows, '2026-09-10T00:00:00+00:00')
    directory = root / 'retry-costs'
    ledger_path = directory / 'attempts.jsonl'
    ledger = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    for attempt in ledger:
        attempt['sequence'] += 1
    failed_cost = .014096
    ledger.insert(0, {
        **ledger[0], 'sequence': 1, 'attempt_id': 'failed', 'cost_usd': failed_cost,
        'result': {'task_id': 't1', 'error': 'timeout', 'error_kind': 'unavailable', 'cost_usd': failed_cost},
    })
    ledger_path.write_text(''.join(json.dumps(attempt) + '\n' for attempt in ledger))
    costs = [attempt['cost_usd'] for attempt in ledger]
    # SQLite and Python can use different floating point accumulation methods.
    assert math.fsum(costs) != sum(costs)
    summary_path = directory / 'summary.json'
    summary = json.loads(summary_path.read_text())
    summary['spent_cost_usd'] = math.fsum(costs)
    summary['models']['mock-model']['cost_usd'] = math.fsum(costs) + cost_adjustment
    summary_path.write_text(json.dumps(summary))
    data, warnings = collect_observations(_release(), tmp_path, _items())
    assert bool(data['configs']) is accepted, warnings
    if accepted:
        assert not warnings
    else:
        assert any('Model cost disagrees' in warning for warning in warnings)

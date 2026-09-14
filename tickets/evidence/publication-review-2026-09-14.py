"""Independent replay of the published V1.2 cohort; imports no benchmark grader."""

from collections import Counter, defaultdict
from decimal import Decimal
from itertools import combinations
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'results/runs/1.2.0/2026-09-12-first-campaign'
ITEMS = json.loads((ROOT / 'dataset/borderbench-v1.2/manifest.json').read_text())['tasks']
REPORT = json.loads((RUN / 'final_results.json').read_text())
AXES = ('has_border', 'border_sides', 'stroke_style', 'stroke_width',
        'corner_radius', 'corner_uniformity', 'elevation')
BY_ID = {item['taskId']: item for item in ITEMS}
LABELS = {axis: list(dict.fromkeys(item['groundTruth'][axis] for item in ITEMS)) for axis in AXES}


def unique_object(pairs):
    assert len({key for key, _ in pairs}) == len(pairs), 'Duplicate JSON key'
    return dict(pairs)


def label_key(value):
    return str(value).lower() if isinstance(value, bool) else value


def verify_measures(rows, published):
    expected = {'count': len(rows)}
    for axis in ('exact', *AXES):
        flags = [all(row['flags'].values()) if axis == 'exact' else row['flags'][axis] for row in rows]
        expected[axis] = round(sum(flags) / len(rows), 4) if rows else None
    assert published['metrics'] == expected, ('metrics', expected, published['metrics'])
    for section, axes in [('attributes', AXES), ('border_present', ('border_sides', 'stroke_style', 'stroke_width'))]:
        selected = rows if section == 'attributes' else [row for row in rows if row['gt']['has_border']]
        for axis in axes:
            counts = {label_key(label): sum(row['gt'][axis] == label for row in selected) for label in LABELS[axis]}
            confusion = {label_key(label): dict(Counter(label_key(row['prediction'][axis]) for row in selected
                                                       if row['gt'][axis] == label)) for label in LABELS[axis]}
            recall = {label: confusion[label].get(label, 0) / count if count else None for label, count in counts.items()}
            observed = [value for value in recall.values() if value is not None]
            correct = sum(row['flags'][axis] for row in selected)
            diagnostics = dict(count=len(selected), accuracy=correct / len(selected) if selected else None,
                               balanced_accuracy_observed_classes=sum(observed) / len(observed) if observed else None,
                               observed_class_count=len(observed), defined_class_count=len(LABELS[axis]),
                               majority_baseline=max(counts.values()) / len(selected) if selected else None,
                               class_count=counts, class_recall=recall, confusion=confusion)
            saved = published['diagnostics'][section][axis]
            for key, value in diagnostics.items():
                if isinstance(value, float):
                    assert abs(value - saved[key]) < 1e-12, (section, axis, key)
                else:
                    assert saved[key] == value, (section, axis, key)


def main():
    cohort = REPORT['comparison']['task_ids']
    shuffled = sorted(BY_ID)
    random.Random(0).shuffle(shuffled)
    assert sorted(shuffled[:128]) == cohort
    assert len(ITEMS) == 477 and len(BY_ID) == 477
    assert len({item['prompt'] for item in ITEMS}) == 1
    shapes = defaultdict(list)
    for item in ITEMS:
        shapes[item['design']['recipeId']].append(item)
    for rows in shapes.values():
        assert len(rows) == 9
        assert len({(row['groundTruth']['theme'], row['groundTruth']['elevation']) for row in rows}) == 9
        assert len({tuple(row['groundTruth'][axis] for axis in AXES[:-1]) for row in rows}) == 1
    assert len(shapes) == 53

    attempts = [json.loads(line) for line in (RUN / 'attempts.jsonl').read_text().splitlines()]
    assert len(attempts) == 1664
    assert len({(row['model_id'], row['task_id']) for row in attempts}) == 1664
    archived = {row['attempt_id']: row for row in attempts}
    rows_by_model = defaultdict(list)
    for observation in REPORT['results']:
        result = observation['result']
        gt = BY_ID[result['task_id']]['groundTruth']
        parsed = json.loads(result['raw_prediction'], object_pairs_hook=unique_object)
        assert set(parsed) == set(AXES) and type(parsed['has_border']) is bool
        assert all(isinstance(parsed[axis], str) for axis in AXES[1:])
        parsed = {axis: parsed[axis].strip().lower() if axis != 'has_border' else parsed[axis] for axis in AXES}
        assert all(parsed[axis] in LABELS[axis] for axis in AXES)
        flags = {axis: parsed[axis] == gt[axis] for axis in AXES}
        assert all(result[axis + '_gt'] == gt[axis] and result['predicted_' + axis] == parsed[axis]
                   and result[axis + '_correct'] is flags[axis] for axis in AXES)
        assert result['all_correct'] is all(flags.values())
        assert result['error'] is None and result['error_kind'] is None
        assert result['request_attempts'] == 1 and result['unmetered_attempts'] == 0
        assert archived[observation['source_attempt_id']]['result'] == result
        rows_by_model[observation['model_id']].append(dict(gt=gt, prediction=parsed, flags=flags, result=result))

    blocks = defaultdict(list)
    for item in ITEMS:
        for block in item['design']['matchedBlocks']:
            axis = block['axis']
            if axis in AXES:
                gt = item['groundTruth']
                blocks[(axis, block['id'], gt['theme'], None if axis == 'elevation' else gt['elevation'])].append(item['taskId'])
    models, total_cost = [], Decimal(0)
    for model in REPORT['models']:
        rows = rows_by_model[model['model_id']]
        assert sorted(row['result']['task_id'] for row in rows) == cohort
        verify_measures(rows, model)
        for axis, groups in model['groups'].items():
            for group in groups:
                verify_measures([row for row in rows if row['gt'][axis] == group['label']], group)
        selected = {row['result']['task_id']: row for row in rows}
        matched = defaultdict(lambda: dict(expected_blocks=0, complete_blocks=0, correct_blocks=0,
                                           level_pairs=0, correct_pairs=0))
        for (axis, *_), ids in blocks.items():
            if len(ids) < 2:
                continue
            stats = matched[axis]
            stats['expected_blocks'] += 1
            if set(ids) <= selected.keys():
                stats['complete_blocks'] += 1
                flags = [selected[task]['flags'][axis] for task in ids]
                stats['correct_blocks'] += all(flags)
                for pair in combinations(flags, 2):
                    stats['level_pairs'] += 1
                    stats['correct_pairs'] += all(pair)
        for axis, stats in matched.items():
            stats['all_levels_correct_rate'] = stats['correct_blocks'] / stats['complete_blocks'] if stats['complete_blocks'] else None
            stats['both_levels_correct_pair_rate'] = stats['correct_pairs'] / stats['level_pairs'] if stats['level_pairs'] else None
            assert model['matched_blocks'][axis] == stats
        config = model['model_config']
        cost = Decimal(0)
        for row in rows:
            response = row['result']
            amount = (Decimal(response['input_tokens']) * Decimal(str(config['input_per_m']))
                      + Decimal(response['output_tokens']) * Decimal(str(config['output_per_m']))) / 1_000_000
            assert abs(float(amount) - response['cost_usd']) < 1e-12
            cost += amount
        assert abs(float(cost / len(rows)) - model['mean_api_response_cost_usd']) < 1e-12
        total_cost += cost
        models.append(dict(model_id=model['model_id'], exact_count=sum(all(row['flags'].values()) for row in rows),
                           sample_count=len(rows), cost_usd=str(cost)))
    assert abs(float(total_cost) - REPORT['campaign']['spent_cost_usd']) < 1e-10
    print(json.dumps(dict(audit_date='2026-09-14', release='1.2.0', full_count=477, cohort_count=len(cohort),
                          response_count=sum(len(rows) for rows in rows_by_model.values()),
                          recipe_count=len(shapes), observed_recipe_count=len({BY_ID[task]['design']['recipeId'] for task in cohort}),
                          class_counts={axis: dict(Counter(label_key(BY_ID[task]['groundTruth'][axis]) for task in cohort)) for axis in AXES},
                          complete_matched_blocks={axis: stats['complete_blocks'] for axis, stats in matched.items()},
                          exact_total_cost_usd=str(total_cost), models=models,
                          outcome='All raw grades, metrics, subgroup diagnostics, matched blocks, and costs agree.'), indent=2))


if __name__ == '__main__':
    main()

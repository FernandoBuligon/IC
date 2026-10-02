#!/usr/bin/env python3
"""Validate the published metrics and print comparisons without changing files."""

import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
AD = set('bottle cable capsule carpet grid hazelnut leather metal_nut pill screw tile toothbrush transistor wood zipper'.split())
LOCO = set('breakfast_box juice_bottle pushpins screw_bag splicing_connectors'.split())


def read_csv(path, categories):
    with (ROOT / path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    names = [row['category'] for row in rows]
    if len(names) != len(set(names)) or set(names) - {'Mean'} != categories:
        raise ValueError(f'Unexpected or duplicate categories: {path}')
    return {row['category']: row for row in rows}


def close(actual, expected, label, tolerance=1e-12):
    if not math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=tolerance):
        raise ValueError(f'{label}: {actual} != {expected}')


def read_json(path):
    return json.loads((ROOT / path).read_text())


def main():
    manifest = read_json('results/provenance.json')['files']
    if len(manifest) != 45 or len({entry['path'] for entry in manifest}) != 45:
        raise ValueError('Expected 45 distinct source artifacts')
    for entry in manifest:
        data = (ROOT / entry['path']).read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f'Integrity failure: {entry["path"]}')

    pc_ad = read_csv('results/patchcore/patchcore_mvtec_ad_geometry_fixed_summary.csv', AD)
    ea_ad = read_csv('results/efficientad/efficientad_mvtec_ad_results.csv', AD)
    ad_values = {'PatchCore': [], 'EfficientAD-M': []}
    print('MVTec AD: category,patchcore_image,efficientad_image,patchcore_aupro,efficientad_aupro')
    for category in sorted(AD):
        pc = read_json(f'results/patchcore/standardized_eval_geometry_fixed/metrics/{category}/metrics.json')[category]
        run = 'EA002_bottle_full' if category == 'bottle' else f'EA003_{category}_full'
        ea = read_json(f'results/efficientad/{run}/metrics/mvtec_ad/metrics.json')[category]
        for key, source in [('image_auc', 'classification_au_roc'), ('au_pro_03', 'au_pro')]:
            close(pc_ad[category][key], pc[source], f'PC AD {category} {key}')
        for key, source in [('image_auroc', 'classification_au_roc'), ('aupro_fpr_0.3', 'au_pro')]:
            close(ea_ad[category][key], ea[source], f'EA AD {category} {key}', 0.00000051)
        for name, data in [('PatchCore', pc), ('EfficientAD-M', ea)]:
            ad_values[name].append((data['classification_au_roc'], data['au_pro']))
        print(f"{category},{pc['classification_au_roc']:.6f},{ea['classification_au_roc']:.6f},{pc['au_pro']:.6f},{ea['au_pro']:.6f}")
    for name, expected in [('PatchCore', (0.990959, 0.925413)), ('EfficientAD-M', (0.990052, 0.936177))]:
        means = tuple(statistics.mean(v[i] for v in ad_values[name]) for i in (0, 1))
        for actual, value in zip(means, expected):
            close(actual, value, f'{name} AD report mean', 0.00000051)
        if name == 'EfficientAD-M':
            for actual, key in zip(means, ('image_auroc', 'aupro_fpr_0.3')):
                close(actual, ea_ad['Mean'][key], f'EA AD CSV mean {key}', 0.00000051)
        print(f'{name}: Image AUROC={means[0]:.6f}, AU-PRO@0.3={means[1]:.6f}')

    pc_loco = read_csv('results/patchcore_loco/patchcore_loco_summary_geometry_fixed.csv', LOCO)
    ea_loco = read_csv('results/efficientad_loco/efficientad_loco_summary.csv', LOCO)
    comparison = read_csv('results/loco_patchcore_vs_efficientad.csv', LOCO)
    sources = [
        ('patchcore', pc_loco, 'results/patchcore_loco/PCL001/standardized_eval_geometry_fixed/metrics/mvtec_loco', (0.737883, 0.501778)),
        ('efficientad', ea_loco, 'results/efficientad_loco/EAL_full_evaluation/metrics/mvtec_loco', (0.894370, 0.798023)),
    ]
    print('\nMVTec LOCO AD: means over five categories')
    for name, rows, directory, expected in sources:
        for category in sorted(LOCO):
            data = read_json(f'{directory}/{category}/metrics.json')
            for suffix, kind in [('logical', 'logical_anomalies'), ('structural', 'structural_anomalies'), ('mean', 'mean')]:
                close(rows[category][f'image_auc_{suffix}'], data['classification']['auc_roc'][kind], f'{name} {category} image {suffix}')
                close(rows[category][f'spro_005_{suffix}'], data['localization']['auc_spro'][kind]['0.05'], f'{name} {category} sPRO {suffix}')
            for metric in ('image_auc', 'spro_005'):
                close(rows[category][f'{metric}_mean'], (float(rows[category][f'{metric}_logical']) + float(rows[category][f'{metric}_structural'])) / 2, f'{name} {category} type mean')
        for metric, value in zip(('image_auc_mean', 'spro_005_mean'), expected):
            close(statistics.mean(float(rows[c][metric]) for c in LOCO), value, f'{name} LOCO report mean', 0.00000051)
        for metric in ('image_auc', 'spro_005'):
            print(name, metric, ', '.join(f'{kind}={statistics.mean(float(rows[c][f"{metric}_{kind}"]) for c in LOCO):.6f}' for kind in ('logical', 'structural', 'mean')))
    for category in LOCO:
        for metric in ('image_auc', 'spro_005'):
            for kind in ('logical', 'structural', 'mean'):
                key = f'{metric}_{kind}'
                pc = float(pc_loco[category][key])
                ea = float(ea_loco[category][key])
                for prefix, value in [('patchcore', pc), ('efficientad', ea), ('delta_ea_minus_pc', ea - pc)]:
                    close(comparison[category][f'{prefix}_{key}'], value, f'LOCO comparison {category} {prefix} {key}')
    print('\nOK: 45 unchanged artifacts; 40 category evaluations; CSVs, comparisons and report means verified.')


if __name__ == '__main__':
    main()

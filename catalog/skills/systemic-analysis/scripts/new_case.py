#!/usr/bin/env python3
"""Gera o esqueleto de um novo caso, sem inventar variáveis ou evidências."""
import argparse
import json
from pathlib import Path


def skeleton(case_id, name, problem, objective):
    return {
        'workflow_version': '1.0.0', 'case_id': case_id, 'status': 'draft',
        'system': {
            'name': name, 'problem': problem, 'objective': objective,
            'horizon': 'UNKNOWN', 'boundary_included': [], 'boundary_excluded': [],
            'stakeholders': [], 'method_fit': 'unknown'
        },
        'evidence': [],
        'iceberg': {key: [] for key in ('events', 'patterns', 'structures', 'mental_models')},
        'variables': [], 'links': [], 'loops': [], 'archetypes': [],
        'behavior_hypotheses': [], 'leverage_points': [], 'roadmap': [],
        'simulation': {'status': 'not_performed', 'model_type': None,
                       'validation_evidence_ids': [], 'results': []},
        'review': {'external_reviewer': None, 'external_evidence': None,
                   'limitations': ['A análise ainda não foi iniciada.'],
                   'next_gate': 'G0: delimitar o sistema.'}
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('id', 'name', 'problem', 'objective'):
        p.add_argument('--' + arg, required=True)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args(argv)
    if a.output.exists():
        p.error(f'o ficheiro já existe: {a.output} (não será substituído)')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(skeleton(a.id, a.name, a.problem, a.objective),
                                  ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Caso criado (draft): {a.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

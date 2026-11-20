#!/usr/bin/env python3
"""Gera um diagrama causal Mermaid a partir do case.json (fonte única)."""
import argparse
import json
from pathlib import Path


def escape_label(text):
    return str(text).replace('\\', '\\\\').replace('"', "'").replace('<', '‹').replace('>', '›').replace('\n', ' ')


def render(case):
    lines = ['flowchart LR',
             '  %% Causal loop diagram qualitativo; não é um modelo de simulação calibrado.']
    idmap = {}
    for idx, variable in enumerate(case.get('variables', []), 1):
        node = f'N{idx}'
        idmap[variable['id']] = node
        lines.append(f'  {node}["{escape_label(variable["name"])}"]')
    for link in case.get('links', []):
        start, end = idmap.get(link.get('source')), idmap.get(link.get('target'))
        if not start or not end:
            raise ValueError(f'Ligação {link.get("id")} refere variável inexistente')
        polarity = link['polarity']
        label = polarity + (' / atraso' if link.get('delay') in ('possible', 'confirmed') else '')
        lines.append(f'  {start} -- "{escape_label(label)}" --> {end}')
    lines.append('  %% Os loops são guardados em case.json e verificados pelo validador.')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args(argv)
    case = json.loads(a.input.read_text(encoding='utf8'))
    result = render(case)
    if a.output.resolve() == a.input.resolve():
        p.error('não é permitido substituir o case.json')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(result, encoding='utf-8')
    print(f'Diagrama gerado: {a.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

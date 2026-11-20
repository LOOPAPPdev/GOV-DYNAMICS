#!/usr/bin/env python3
"""Validador determinístico de integridade da análise LOOP.

Não prova a veracidade empírica das relações causais. Nenhuma dependência externa.
"""
import argparse
import json
import sys
from pathlib import Path

EXPECTED_SECTIONS = (
    'workflow_version', 'case_id', 'status', 'system', 'evidence', 'iceberg',
    'variables', 'links', 'loops', 'archetypes', 'behavior_hypotheses',
    'leverage_points', 'roadmap', 'simulation', 'review'
)
ICEBERG_SECTIONS = ('events', 'patterns', 'structures', 'mental_models')
ID_COLLECTIONS = ('evidence', 'variables', 'links', 'loops', 'archetypes',
                  'behavior_hypotheses', 'leverage_points', 'roadmap')


def validate(case, strict=False):
    errors, warnings = [], []
    if not isinstance(case, dict):
        return ['Raiz: esperado objeto JSON'], warnings
    for key in EXPECTED_SECTIONS:
        if key not in case:
            errors.append(f'Campo obrigatório ausente: {key}')
    if errors:
        return errors, warnings
    if case['workflow_version'] != '1.0.0':
        errors.append('workflow_version deve ser 1.0.0')
    if case['status'] not in ('draft', 'review_ready', 'externally_validated'):
        errors.append('status inválido')
    sysobj = case['system']
    if not isinstance(sysobj, dict):
        return ['system deve ser objeto'], warnings
    for key in ('name', 'problem', 'objective', 'horizon', 'boundary_included',
                'boundary_excluded', 'stakeholders', 'method_fit'):
        if key not in sysobj:
            errors.append(f'system.{key} ausente')
    if errors:
        return errors, warnings
    if sysobj['method_fit'] not in ('high', 'medium', 'low', 'unknown'):
        errors.append('system.method_fit inválido')
    for key in ('name', 'problem', 'objective'):
        if not isinstance(sysobj[key], str) or not sysobj[key].strip():
            errors.append(f'system.{key}: texto obrigatório')
    for key in ('boundary_included', 'boundary_excluded', 'stakeholders'):
        if not isinstance(sysobj[key], list):
            errors.append(f'system.{key}: lista obrigatória')
    if not isinstance(case['iceberg'], dict):
        errors.append('iceberg deve ser objeto')
        return errors, warnings
    for key in ICEBERG_SECTIONS:
        if not isinstance(case['iceberg'].get(key), list):
            errors.append(f'iceberg.{key}: lista obrigatória')
    for key in ID_COLLECTIONS:
        if not isinstance(case[key], list):
            errors.append(f'{key}: lista obrigatória')
    if errors:
        return errors, warnings

    indexes = {}
    all_ids = set()
    for collection in ID_COLLECTIONS:
        indexes[collection] = {}
        for row in case[collection]:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
                errors.append(f'{collection}: elemento sem id válido')
                continue
            item_id = row['id']
            if item_id in all_ids:
                errors.append(f'ID duplicado: {item_id}')
            all_ids.add(item_id)
            indexes[collection][item_id] = row

    evidences = indexes['evidence']
    variables = indexes['variables']
    links = indexes['links']
    loops = indexes['loops']
    leverage = indexes['leverage_points']

    def check_evidence(owner, evidence_ids):
        if not isinstance(evidence_ids, list):
            errors.append(f'{owner}.evidence_ids deve ser lista')
            return
        for evidence_id in evidence_ids:
            if evidence_id not in evidences:
                errors.append(f'{owner}: evidência inexistente {evidence_id}')

    for ev in evidences.values():
        if ev.get('status') not in ('verified', 'unverified'):
            errors.append(f"{ev['id']}: status de evidência inválido")
        if ev.get('kind') == 'assumption' and ev.get('status') == 'verified':
            errors.append(f"{ev['id']}: hipótese não pode ser marcada como medição verificada")
        if ev.get('status') == 'verified' and not ev.get('source'):
            errors.append(f"{ev['id']}: evidência verificada sem fonte")
        if ev.get('status') == 'unverified':
            warnings.append(f"{ev['id']}: evidência ainda não verificada")

    for layer in ICEBERG_SECTIONS:
        for idx, item in enumerate(case['iceberg'][layer]):
            if not isinstance(item, dict):
                errors.append(f'iceberg.{layer}[{idx}]: esperado objeto')
                continue
            if not item.get('text'):
                errors.append(f'iceberg.{layer}[{idx}]: texto ausente')
            check_evidence(f'iceberg.{layer}[{idx}]', item.get('evidence_ids', []))

    for v in variables.values():
        if v.get('kind') not in ('stock', 'flow', 'auxiliary', 'exogenous', 'unknown'):
            errors.append(f"{v['id']}: tipo de variável inválido")
        check_evidence(v['id'], v.get('evidence_ids', []))

    for lnk in links.values():
        for field in ('source', 'target'):
            if lnk.get(field) not in variables:
                errors.append(f"{lnk['id']}: {field} aponta para variável inexistente {lnk.get(field)}")
        if lnk.get('polarity') not in ('+', '-', 'unknown'):
            errors.append(f"{lnk['id']}: polaridade inválida")
        if lnk.get('status') not in ('hypothesis', 'supported'):
            errors.append(f"{lnk['id']}: status de relação inválido")
        check_evidence(lnk['id'], lnk.get('evidence_ids', []))
        if lnk.get('status') == 'supported':
            if not any(evidences.get(ref, {}).get('status') == 'verified' for ref in lnk.get('evidence_ids', [])):
                errors.append(f"{lnk['id']}: relação supported sem evidência verificada")
        if lnk.get('status') == 'hypothesis' and not lnk.get('disconfirmation_test'):
            errors.append(f"{lnk['id']}: hipótese sem teste de refutação")

    for loop in loops.values():
        ref_ids = loop.get('link_ids')
        if not isinstance(ref_ids, list) or len(ref_ids) < 2:
            errors.append(f"{loop['id']}: loop exige ao menos duas ligações")
            continue
        if len(set(ref_ids)) != len(ref_ids):
            errors.append(f"{loop['id']}: ligações repetidas no loop")
        if any(ref not in links for ref in ref_ids):
            errors.append(f"{loop['id']}: ligação inexistente no loop")
            continue
        chain = [links[ref] for ref in ref_ids]
        for a, b in zip(chain, chain[1:] + chain[:1]):
            if a.get('target') != b.get('source'):
                errors.append(f"{loop['id']}: circuito não fecha entre {a['id']} e {b['id']}")
        pols = [edge.get('polarity') for edge in chain]
        expected = ('undetermined' if 'unknown' in pols else
                    'balancing' if pols.count('-') % 2 else 'reinforcing')
        if loop.get('classification') != expected:
            errors.append(f"{loop['id']}: tipo {loop.get('classification')} inconsistente; esperado {expected}")
        if loop.get('status') == 'supported' and any(edge.get('status') != 'supported' for edge in chain):
            errors.append(f"{loop['id']}: loop supported contém arestas apenas hipotéticas")

    for arch in indexes['archetypes'].values():
        for lid in arch.get('loop_ids', []):
            if lid not in loops:
                errors.append(f"{arch['id']}: loop inexistente {lid}")
        if arch.get('status') not in ('hypothesis', 'supported', 'rejected'):
            errors.append(f"{arch['id']}: status de arquétipo inválido")
        if not arch.get('disconfirmation_test'):
            errors.append(f"{arch['id']}: falta condição de refutação")

    for hyp in indexes['behavior_hypotheses'].values():
        check_evidence(hyp['id'], hyp.get('evidence_ids', []))
        if not hyp.get('disconfirmation_test'):
            errors.append(f"{hyp['id']}: hipótese sem teste de refutação")

    for lp in leverage.values():
        for vid in lp.get('variable_ids', []):
            if vid not in variables:
                errors.append(f"{lp['id']}: variável inexistente {vid}")
        check_evidence(lp['id'], lp.get('evidence_ids', []))
        if lp.get('priority') not in ('low', 'medium', 'high', 'undetermined'):
            errors.append(f"{lp['id']}: prioridade inválida")

    for action in indexes['roadmap'].values():
        if action.get('leverage_point_id') not in leverage:
            errors.append(f"{action['id']}: ponto de alavancagem inexistente")
        for field in ('action', 'owner', 'indicator', 'checkpoint', 'stop_condition'):
            if not action.get(field):
                errors.append(f"{action['id']}: falta {field}")
        if not isinstance(action.get('approval_required'), bool):
            errors.append(f"{action['id']}: approval_required deve ser booleano")

    simulation = case['simulation']
    if not isinstance(simulation, dict):
        errors.append('simulation deve ser objeto')
    else:
        if simulation.get('status') not in ('not_performed', 'performed'):
            errors.append('simulation.status inválido')
        if simulation.get('status') == 'performed':
            if not simulation.get('model_type') or not simulation.get('validation_evidence_ids') or not simulation.get('results'):
                errors.append('Simulação realizada exige tipo do modelo, evidência de validação e resultados')
        elif simulation.get('results'):
            errors.append('Simulação not_performed não pode conter resultados')
        check_evidence('simulation', simulation.get('validation_evidence_ids', []))

    review = case['review']
    if not isinstance(review, dict):
        errors.append('review deve ser objeto')
    elif case['status'] == 'externally_validated' and not (review.get('external_reviewer') and review.get('external_evidence')):
        errors.append('externally_validated exige revisor externo e referência de evidência')

    if strict:
        if sysobj['method_fit'] == 'unknown' or not sysobj['horizon'].strip() or sysobj['horizon'] == 'UNKNOWN':
            errors.append('G0: adequação e horizonte devem estar definidos')
        if not sysobj['boundary_included'] or not sysobj['stakeholders']:
            errors.append('G0: fronteiras incluídas e stakeholders obrigatórios')
        for layer in ICEBERG_SECTIONS:
            if not case['iceberg'][layer] and sysobj['method_fit'] != 'low':
                errors.append(f'G1: iceberg.{layer} vazio')
        if sysobj['method_fit'] != 'low':
            for collection in ('variables', 'links', 'behavior_hypotheses', 'leverage_points', 'roadmap'):
                if not case[collection]:
                    errors.append(f'Análise incompleta: {collection} vazio')
    else:
        if sysobj['method_fit'] == 'unknown':
            warnings.append('G0 ainda pendente: avaliar adequação da abordagem sistémica')

    if not any(ev.get('status') == 'verified' for ev in evidences.values()):
        warnings.append('Nenhuma evidência empírica verificada: resultados são apenas hipóteses')
    if case['status'] != 'externally_validated':
        warnings.append('O caso não foi validado externamente')
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--strict', action='store_true', help='Exige preenchimento estrutural das etapas')
    args = parser.parse_args(argv)
    try:
        case = json.loads(args.input.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'ERRO: não foi possível ler JSON: {exc}', file=sys.stderr)
        return 2
    errors, warnings = validate(case, strict=args.strict)
    for item in errors:
        print('ERROR:', item)
    for item in warnings:
        print('WARN:', item)
    if errors:
        print(f'FAIL: {len(errors)} erro(s), {len(warnings)} aviso(s)')
        return 1
    print(f'PASS (integridade estrutural): 0 erros, {len(warnings)} aviso(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Read completed matched arms and report identity-start transfer."""
import argparse
import json
from pathlib import Path


def compare(identity_dir, random_dir):
    dirs = [identity_dir, random_dir]
    manifests = [json.loads((d/'manifest.json').read_text()) for d in dirs]
    results = [json.loads((d/'completed.json').read_text()) for d in dirs]
    a, b = manifests
    if [a['arm'], b['arm']] != ['identity','exploratory']:
        raise ValueError('Expected identity, then exploratory run')
    for key in ('seed','groups','generations','training_proposals','evaluation_proposals_per_phase',
                'max_completion','target','model','model_config_sha256','git_commit','adapter_config','packages'):
        if a[key] != b[key]:
            raise ValueError(f'Unmatched experiment: {key}')
    initial_fingerprints = [json.loads((d/'initial_adapter_fingerprints.json').read_text()) for d in dirs]
    if initial_fingerprints[0] != initial_fingerprints[1]:
        raise ValueError('Initial trainable adapter weights differ')
    for key in ('learning_rate','max_steps','per_device_train_batch_size','gradient_accumulation_steps',
                'num_generations','num_iterations','max_completion_length','loss_type','scale_rewards','beta',
                'temperature','top_p','top_k','mask_truncated_completions'):
        if a['grpo_config'][key] != b['grpo_config'][key]:
            raise ValueError(f'Unmatched training configuration: {key}')
    for manifest, result in zip(manifests,results):
        if result['training']['proposals'] != manifest['training_proposals']:
            raise ValueError('Unmatched proposal budget')
        if any(result[phase]['proposals'] != manifest['evaluation_proposals_per_phase'] for phase in ('identity_before','identity_after')):
            raise ValueError('Unmatched evaluation budget')
    baseline = [r['identity_before']['pass_at_1'] for r in results]
    final = [r['identity_after']['pass_at_1'] for r in results]
    return {'identity': results[0], 'exploratory': results[1],
            'exploratory_minus_identity_pass_at_1': final[1]-final[0],
            'baseline_adjusted_difference': (final[1]-baseline[1])-(final[0]-baseline[0])}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('identity',type=Path)
    p.add_argument('exploratory',type=Path)
    args=p.parse_args()
    print(json.dumps(compare(args.identity,args.exploratory),indent=2))

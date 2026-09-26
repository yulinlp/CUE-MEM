"""Prepare published CUE-Mem dialogue JSONs for the experiment runners.

Media stay in the downloaded dataset. Only JSON files are copied, with
repository-relative media paths resolved to absolute local paths.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def prepare(dataset_root: Path, output_root: Path) -> dict:
    dataset_root = dataset_root.expanduser().resolve()
    output_root = output_root.expanduser().resolve()
    sources = sorted((dataset_root / 'data/dialog/base').glob('*.json'))
    if not sources:
        raise ValueError('No JSON files found under dataset_root/data/dialog/base')
    if output_root == dataset_root or dataset_root in output_root.parents:
        raise ValueError('Use an output directory outside the downloaded dataset')
    destination = output_root / 'data/dialog/base'
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f'Output is not empty: {destination}')
    missing = set()
    media = set()

    def rewrite(value):
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, str):
            relative = value.replace('\\', '/').removeprefix('./')
            if relative.startswith('data/') and Path(relative).suffix.lower() in {
                '.jpg', '.jpeg', '.png', '.webp', '.gif', '.wav', '.mp3', '.flac', '.ogg', '.m4a', '.mp4'
            }:
                target = (dataset_root / relative).resolve()
                if not target.is_relative_to(dataset_root):
                    raise ValueError(f'Media path escapes dataset root: {relative}')
                media.add(relative)
                if not target.is_file():
                    missing.add(relative)
                return str(target)
        return value

    # Validate all input JSONs before creating output files.
    documents = [(p.name, rewrite(json.loads(p.read_text(encoding='utf-8')))) for p in sources]
    destination.mkdir(parents=True, exist_ok=True)
    for name, document in documents:
        (destination / name).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = {'profiles': len(documents), 'referenced_media': len(media),
              'missing_media': sorted(missing), 'dialog_dir': str(destination)}
    (output_root / 'dataset_preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = prepare(args.dataset_root, args.output_root)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')
    print(f"Prepared {report['profiles']} profile files in {report['dialog_dir']}")
    print(f"Referenced media: {report['referenced_media']}; missing: {len(report['missing_media'])}")
    if report['missing_media']:
        print('See dataset_preparation.json. Download missing media before multimodal experiments.')


if __name__ == '__main__':
    main()

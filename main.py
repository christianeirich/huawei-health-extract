#!/usr/bin/env python3
"""
Export weight and body-fat readings from Huawei Health JSON files into per-user CSVs
with epoch-millisecond timestamps, ready for TaskerHealthConnect ingestion.
"""

import sys
import json
import csv
import re

from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Tuple, Any

FILENAME_CLEANUP = re.compile(r'[^0-9A-Za-z._-]')


def generate_user_id(record: Dict[str, Any], data: Dict[str, Any]) -> str:
    """
Derive a stable user identifier from JSON record fields.
Prefers 'subUser', then 'extendAttribute', else falls back to deviceCode|gender.
    """
    if 'subUser' in record:
        return str(record['subUser'])
    ext = (data.get('extendAttribute') or '').strip()
    if ext and ext not in {'0', 'null', 'None'}:
        return ext
    return f"{record.get('deviceCode', 'dev')}|g{data.get('gender', 'u')}"


def parse_weight_bodyfat_records(json_path: Path) -> List[Tuple[str, int, float, float]]:
    """
Read a Huawei Health JSON file and extract all weight/body-fat entries.
Returns a list of tuples: (user_id, timestamp_ms, weight_kg, fat_pct).
    """
    entries: List[Tuple[str, int, float, float]] = []
    try:
        blob = json.loads(json_path.read_text(encoding='utf-8'))
    except Exception:
        return entries
    records = blob if isinstance(blob, list) else [blob]
    for rec in records:
        if rec.get('type') != 10006:
            continue
        for sp in rec.get('samplePoints', []):
            if sp.get('key') != 'WEIGHT_BODYFAT_BROAD':
                continue
            ms = sp.get('startTime')
            if not isinstance(ms, int):
                continue
            try:
                data = json.loads(sp['value'])
            except Exception:
                continue
            weight = data.get('bodyWeight')
            fat = data.get('bodyFatRate')
            if weight is None and fat is None:
                continue
            user = generate_user_id(rec, data)
            entries.append((user, ms, weight or 0.0, fat or 0.0))
    return entries


def collect_per_user(records_folder: Path) -> Dict[str, Dict[int, Tuple[float, float]]]:
    """
Scan all JSON files in the given folder and organize entries by user and timestamp.
Returns a mapping: user_id → {timestamp_ms: (weight_kg, fat_pct)}.
    """
    per_user: Dict[str, Dict[int, Tuple[float, float]]] = defaultdict(dict)
    for json_file in records_folder.glob('*.json'):
        for user, ts, w, f in parse_weight_bodyfat_records(json_file):
            per_user[user][ts] = (w, f)
    return per_user


def write_user_csvs(per_user: Dict[str, Dict[int, Tuple[float, float]]], output_folder: Path) -> None:
    """
Write one CSV per user into output_folder, with columns: timestamp,weight_kg,fat_pct.
Filenames are sanitized user IDs.
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    for user, records in per_user.items():
        safe_name = FILENAME_CLEANUP.sub('_', user)
        csv_path = output_folder / f"{safe_name}.csv"
        with csv_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'weight_kg', 'fat_pct'])
            for ts in sorted(records):
                w, f = records[ts]
                writer.writerow([ts, f"{w:.2f}", f"{f:.1f}"])
        print(f"wrote {csv_path}")


def main() -> None:
    """
Command-line entry point.
Usage: python main.py <json_folder> [<out_folder>]
Defaults to writing CSVs to an 'out/' folder.
    """
    if not (2 <= len(sys.argv) <= 3):
        sys.exit("usage: python main.py <json_folder> [<out_folder>]")
    src = Path(sys.argv[1]).expanduser().resolve()
    if not src.is_dir():
        sys.exit(f"{src} is not a directory")
    base = Path(__file__).parent.resolve()
    out = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) == 3 else base / 'out'
    user_data = collect_per_user(src)
    write_user_csvs(user_data, out)


if __name__ == '__main__':
    main()

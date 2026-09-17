"""Snapshot Dfam metadata for the 1,220 interspersed names: summaries, full records without sequences, the classification tree and the release."""
import csv, gzip, hashlib, json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/dfam_snapshot')
CENSUS = Path('/workspaces/Meta-Aging/01_modules/te-tracks/docs/_internal/redesign-2026-09/taxonomy/dfam_census_1220_20260917.tsv')
API = 'https://dfam.org/api'
DROP = {'consensus_sequence', 'model_mask', 'hmm_general_threshold', 'search_stages', 'buffer_stages'}

def get(path, params=None, tries=4):
    url = API + path + ('?' + urllib.parse.urlencode(params) if params else '')
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as response:
                return json.load(response)
        except Exception as error:
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))

started = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
version = get('/version')
classes = get('/classes')
names = [row['rmsk_name'] for row in csv.DictReader(CENSUS.open(), delimiter='\t')]
assert len(names) == 1220 and len(set(names)) == 1220
summaries, records, errors = {}, {}, []
for i, name in enumerate(names, 1):
    try:
        data = get('/families', {'name': name, 'format': 'summary'})
    except Exception as error:
        errors.append({'name': name, 'stage': 'summary', 'error': str(error)}); continue
    results = data.get('results', [])
    summaries[name] = results
    wanted = [r for r in results if r['name'] == name] or [r for r in results if r['name'].startswith(name + '_')]
    for r in wanted:
        acc = r['accession']
        if acc in records:
            continue
        try:
            full = get('/families/' + acc)
        except Exception as error:
            errors.append({'name': name, 'accession': acc, 'stage': 'record', 'error': str(error)}); continue
        records[acc] = {k: v for k, v in full.items() if k not in DROP}
    if i % 100 == 0:
        print(f'{i} names, {len(records)} records, {len(errors)} errors', flush=True)
finished = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
snapshot = {'version': version, 'classes': classes, 'summaries': summaries, 'records': records}
payload = json.dumps(snapshot, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
target = OUT / 'dfam_interspersed_mm39_snapshot.json.gz'
with gzip.GzipFile(target, 'wb', mtime=0) as handle:
    handle.write(payload)
provenance = {
    'endpoint': API, 'dfam_version': version, 'fetch_started': started, 'fetch_finished': finished,
    'names_queried': len(names), 'names_with_results': sum(1 for v in summaries.values() if v),
    'records_fetched': len(records), 'errors': errors,
    'dropped_record_fields': sorted(DROP),
    'payload_sha256': hashlib.sha256(payload).hexdigest(), 'payload_bytes': len(payload),
    'file_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'file_bytes': target.stat().st_size,
    'census_sha256': hashlib.sha256(CENSUS.read_bytes()).hexdigest(),
}
(OUT / 'dfam_interspersed_mm39_snapshot.provenance.json').write_text(json.dumps(provenance, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: v for k, v in provenance.items() if k != 'errors'}, indent=1))
print('errors', len(errors))

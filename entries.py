import json

with open('entries.ndjson') as f:
    lines = f.read().strip().split('\n')

entries = [json.loads(entry) for entry in lines]



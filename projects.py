import json

with open('projects.ndjson') as f:
    lines = f.read().strip().split('\n')

projects = [json.loads(project) for project in lines]



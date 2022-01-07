from pydantic import BaseModel
from typing import List, Optional
from pendulum.datetime import DateTime

import json

class Project(BaseModel):
    name: str
    id: int
    wid: int
    active: bool
    hex_color: str


class Entry(BaseModel):
    description: str
    project: Optional[Project]
    start: DateTime
    stop: DateTime
    duration: int
    id: int
    tags: List[str]



def _read_ndjson(path: str) -> List[dict]:
    with open(path) as f:
        lines = f.read().strip().split('\n')
    return [json.loads(line) for line in lines]


entries = _read_ndjson('entries.ndjson')
projects = _read_ndjson('projects.ndjson')

def raw_to_entry(e: dict) -> Entry:
    return Entry(**e, project=project_by_id.get(e['pid']))

def raw_to_project(p: dict) -> Project:
    return Project(**p['project'])

projects = [raw_to_project(p) for p in reversed(projects)]
project_by_id = {project.id: project for project in projects}
entries = [
    raw_to_entry(e)
    for e in reversed(entries)
    # a few records (12 in my case) are broken and have "stop": null. this works around that
    if e['stop']
]


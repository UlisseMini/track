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


projects = [Project(**p['project']) for p in projects]
project_by_id = {project.id: project for project in projects}
entries = [
    Entry(
        **e,
        project=project_by_id.get(e['pid'])
    )
    for e in entries
    # a few records (12 in my case) are broken and have "stop": null. this works around that
    if e['stop']
]


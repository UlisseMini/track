from entries import entries
from projects import projects

from pydantic import BaseModel
from typing import List, Optional
from pendulum.datetime import DateTime

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


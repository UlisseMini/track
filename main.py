from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine('postgresql://postgres:postgres@127.0.0.1/postgres')
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, TIMESTAMP, ARRAY, ForeignKey
from sqlalchemy.orm import relationship

class Entry(Base):
    __tablename__ = 'toggl_entries'

    id = Column(BigInteger, primary_key=True)
    pid = Column(BigInteger, ForeignKey('toggl_projects.id'), index=True)
    description = Column(String)
    start = Column(TIMESTAMP(timezone=True))
    stop = Column(TIMESTAMP(timezone=True))
    duration = Column(Integer)
    tags = Column(ARRAY(String))
    # TODO
    # project = relationship("Project", back_populates=)


class Project(Base):
    __tablename__ = 'toggl_projects'

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    wid = Column(BigInteger)
    active = Column(Boolean)
    hex_color = Column(String(7))



from toggl.api import models
from toggl import api
import pendulum
import json
from typing import List, Optional
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import class_mapper

def latest_entry(db):
    row = db.execute(select(Entry).order_by(Entry.start.desc())).first()
    if row is not None:
        entry = row[0]
        return entry


def raw_to_project(project):
    return Project(
        id = project.id, name = project.name, wid = project.wid,
        active = project.active, hex_color = project.hex_color,
    )


def raw_to_entry(entry, project_ids: set) -> Entry:
    return Entry(
        description = entry.description,
        start = entry.start,
        stop = entry.stop,
        duration = entry.duration,
        id = entry.id,
        pid = entry.pid if entry.pid in project_ids else None,
        tags = list(entry.tags),
    )

def main(db: Session):
    # 1. Create tables if needed
    print('Creating tables...')
    Base.metadata.create_all(bind=engine)
    print('done')

    # 2. Update projects
    print('Getting projects... ', end='', flush=True)
    project_ids = set()
    for project in models.Project.objects.all():
        project_ids.add(project.id)
        db_project = raw_to_project(project)
        db.merge(db_project)

    db.commit()
    print('done')

    # 3. Update (or get) entries
    latest = latest_entry(db)

    # max toggl api is 1 year ago, so if we have no latest we fetch data from start
    now = pendulum.now()
    start = latest.start if latest else now.subtract(years=1)
    print(f'Getting entries from {start} to now...')

    entries = models.TimeEntry.objects.all_from_reports(start=start, stop=now) # type: ignore
    for n, entry in enumerate(entries):
        db_entry = raw_to_entry(entry, project_ids)
        print(f'Entry {n} days left {(db_entry.start-start).in_days()}')
        db.merge(db_entry)

    print(f'Commiting entries...')
    db.commit()
    print('done')


if __name__ == '__main__':
    with SessionLocal() as db:
        main(db)

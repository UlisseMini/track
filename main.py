from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine('postgresql://postgres:postgres@127.0.0.1/postgres')
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, ARRAY, ForeignKey
from sqlalchemy.orm import relationship

class Entry(Base):
    __tablename__ = 'toggl_entries'

    id = Column(BigInteger, primary_key=True)
    pid = Column(BigInteger, ForeignKey('toggl_projects.id'), index=True)
    description = Column(String)
    start = Column(DateTime)
    stop = Column(DateTime)
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
    return row[0]


def raw_to_model(raw, model):
    return model(**{
        k: v for k,v in raw.to_dict().items()
        if k in class_mapper(model).attrs.keys()
    })


def main(db: Session):
    # 1. Create tables if needed
    print('Creating tables...')
    Base.metadata.create_all(bind=engine)
    print('done')

    # 2. Update projects
    print('Getting projects... ', end='', flush=True)
    for project in models.Project.objects.all():
        db_project = raw_to_model(project, Project)
        db.merge(db_project)

    db.commit()
    print('done')

    # 3. Update (or get) entries
    latest = latest_entry(db)

    # max toggl api is 1 year ago, so if we have no latest we fetch data from start
    start = latest.start if latest else pendulum.now().subtract(years=1)
    now = pendulum.now()
    # TODO: Progressbar dates
    print(f'Getting entries from {start} to now...')
    num = 1
    for entry in models.TimeEntry.objects.all_from_reports(start=start, stop=now): # type: ignore
        db_entry = raw_to_model(entry, Entry)
        print(f'Updating entries... added {num}', end='\r', flush=True)
        num += 1
        db.merge(db_entry)
        db.commit()

    print(' done')


if __name__ == '__main__':
    with SessionLocal() as db:
        main(db)

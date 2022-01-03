from toggl import api
from toggl.api import models
import pendulum
import json

# when I started using toggl (roughly)
now = pendulum.now()
one_year_ago = now - pendulum.duration(years=1)

for entry in models.TimeEntry.objects.all_from_reports(start=one_year_ago, stop=now):
    # print(entry.json(), flush=True)
    print(json.dumps({
        'description': entry.description,
        'start': entry.start.to_iso8601_string(),
        'stop': entry.stop.to_iso8601_string() if entry.stop else None,
        'duration': entry.duration,
        'id': entry.id,
        'pid': entry.pid, # project id
        'tags': list(entry.tags),
    }), flush=True)



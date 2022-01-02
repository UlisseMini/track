from toggl import api, utils
from toggl.api import models
from typing import List

# to adjust for actual sleep time, not lying in bed time
hours_to_fall_asleep = 0.5

entries: List[models.TimeEntry] = api.TimeEntry.objects.all()
sleep = [entry for entry in entries if entry.description == 'sleep']

durations = [s.duration/60/60 - hours_to_fall_asleep for s in sleep]

bedtimes = [s.start.in_tz('local') for s in sleep]
bedtime_hours = [bt.hour + bt.minute/60 for bt in bedtimes]
# bedtime_hours = [f'{bt.hour%12}:{bt.minute}' for bt in bedtimes]
print('bedtime hour', bedtime_hours)
print('hours slept', durations)


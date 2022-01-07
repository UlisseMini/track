"""
Daily goals, fundementally we want something like

for day in days:
    show_sleep_goal_results(day)
    show_coding_goal_results(day)
    ...
"""
from data import entries, projects, Entry
from collections import defaultdict
from enum import IntEnum
from typing import Callable, List, Optional, Tuple, Dict
from pydantic import BaseModel
from datetime import timedelta, datetime
import dominate.tags as t

Day = List[Entry]
Days = Dict[datetime, Day]


# used in filter

BoolFn = Callable[[Entry], bool]

def by_project(name: str) -> BoolFn:
    return lambda e: bool(e.project and e.project.name.lower() == name)

def by_description(description: str) -> BoolFn:
    return lambda e: e.description == description

def in_description(text: str) -> BoolFn:
    return lambda e: text in e.description

def by_any(fns: List[BoolFn]) -> BoolFn:
    return lambda e: any(fn(e) for fn in fns)

def by_any_project(names: List[str]) -> BoolFn:
    return by_any([by_project(name) for name in names])


days: Days = {}

# fill days_dict with empty lists, this is needed since I might skip
# toggl for a day, in which case we want an empty list
start_date = entries[0].start.date()
end_date = entries[-1].start.date()
days_difference = (end_date - start_date).days
for date in (start_date + timedelta(n) for n in range(days_difference+1)):
    days[date] = []

# populate from entries
for entry in entries:
    days[entry.start.date()].append(entry)


class GoalResultEnum(IntEnum):
    SUCCESS = 1
    FAILURE = 2
    NA = 3


class GoalResult(BaseModel):
    result: GoalResultEnum
    hover: str


def bool_goal_result(success: bool) -> GoalResultEnum:
    return GoalResultEnum.SUCCESS if success else GoalResultEnum.FAILURE

Goal = Callable[[Day], GoalResult]

def _get_sleep_entry(day: Day) -> Optional[Entry]:
    sleep_entries = list(filter(by_project('sleep'), day))
    if len(sleep_entries) == 0:
        return None
    else:
        return max(sleep_entries, key=lambda e: e.duration)


goals: List[Goal] = []
def goal(fn: Goal):
    goals.append(fn)
    char = {GoalResultEnum.NA: 'N', GoalResultEnum.FAILURE: 'F', GoalResultEnum.SUCCESS: 'S'}

    results = [(date, fn(day)) for date, day in days.items()]


    text = ''
    text += fn.__doc__ + '\n'
    for _, result in results:
        text += char[result.result]
    fn.text = text

    name = fn.__name__.replace('_', ' ').title()
    html = t.div(
        t.h1(name),
        t.p(fn.__doc__),
        t.div(
            *[t.div(title=f'{date}: {r.hover}', _class=f'sq sq-{r.result}') for date, r in results],
            _class='squares',
        ),
        _class='goal',
    ).render()

    fn.html = html
    return fn


@goal
def bedtime(day: Day) -> GoalResult:
    "Be in bed by 11pm"
    if entry := _get_sleep_entry(day):
        # bedtime start hour, 12< to deal with 1am situations
        # FIXME: 1am will never happen as it'll be considered the next day
        return GoalResult(
            result=bool_goal_result(12 < entry.start.hour < 22),
            hover=f'bed at {entry.start.hour}'
        )

    return GoalResult(result=GoalResultEnum.NA, hover='could not find bedtime')


@goal
def anki_time(day: Day) -> GoalResult:
    "Do anki reviews every day"
    # NOTE: This is an imperfect goal as it doesn't check that I did all my reviews, it's
    # good enough though

    seconds = sum(entry.duration for entry in filter(by_description('anki'), day))
    minutes = seconds / 60
    return GoalResult(result=bool_goal_result(minutes>0), hover=f'{minutes:.0f}m anki')


WORK_PROJECTS = [
    "book-reading", "coding", "goals", "journal",
    "languages", "math", "science", "textbook-problems",
]

@goal
def work_time(day: Day) -> GoalResult:
    "Work 8h/day"
    hours = sum(e.duration for e in filter(by_any_project(WORK_PROJECTS), day)) / 60 / 60
    return GoalResult(result=bool_goal_result(hours>8), hover=f'{hours:.1f}h work')

@goal
def texify_abbot(day: Day) -> GoalResult:
    "Spend some time texifying solutions to abbott's understanding analysis"
    minutes = sum(e.duration for e in filter(in_description('analysis-writing'), day)) / 60
    return GoalResult(result=bool_goal_result(minutes>0), hover=f'{minutes:.0f}m texifying')

@goal
def science_time(day: Day) -> GoalResult:
    "Do 2h science a day"
    seconds = sum(entry.duration for entry in filter(by_project('science'), day))
    hours = seconds / 60 / 60
    return GoalResult(result=bool_goal_result(hours > 2), hover=f'{hours:.1f}h science')


html = '<html lang="en">\n'
html += t.head(
    t.meta(charset='utf-8'),
    t.title('Goals'),
    t.link(rel='stylesheet', href='styles.css')
).render() + '\n'
html += '<body>\n'

for g in goals:
    html += g.html + '\n'

html += '\n</body>'
html += '\n</html>'
print(html)

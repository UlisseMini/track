from toggl.api import models

projects = models.Project.objects.all()
with open('projects.ndjson', 'w') as f:
    for project in projects:
        print(project.json(), file=f)


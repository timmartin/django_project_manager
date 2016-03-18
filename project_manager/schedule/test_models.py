from django.test import TestCase

import datetime

from .models import Task, Resource, Project

class TaskTests(TestCase):
    def test_estimated_end_date(self):
        worker = Resource()

        first_task = Task(name="first",
                          orig_estimate=3,
                          estimate_remaining=3,
                          resource=worker)

        # Start on a Monday
        monday = datetime.date(2016, 2, 22)

        self.assertEqual(first_task.estimated_end_date(monday),
                         datetime.date(2016, 2, 24))

    def test_project_permalink(self):
        """Creating a new project creates a permalink for it"""

        project = Project(name="foo")
        project.save()

        self.assertNotEqual(project.permalink, "")

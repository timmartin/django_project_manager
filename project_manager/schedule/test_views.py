from django.test import Client, TestCase

from .models import Project, Task, Resource
from django.contrib.auth.models import User

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        main_user = User.objects.create_user("main",
                                             "main@example.com",
                                             "mainpassword")

        self.project = Project("My Project")
        self.project.save()

        worker = Resource(name="worker")
        worker.save()

        self.first_task = Task(name="first",
                               orig_estimate=10,
                               estimate_remaining=10,
                               resource=worker,
                               project=self.project)
        self.first_task.save()

    def test_index(self):
        self.client.login(username="main", password="mainpassword")

        response = self.client.get("/schedule/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['resources']),
                         1)

        self.assertEqual(response.context['project'],
                         self.project)

    def test_update_resource_usage(self):
        self.client.login(username="main", password="mainpassword")

        response = self.client.get("/schedule/resource-weekly/view/worker")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["tasks"],
                         [self.first_task])

        response = self.client.post("/schedule/resource-weekly/update",
                                    {'days[AM][0]': self.first_task.pk,
                                     'days[PM][0]': self.first_task.pk,
                                     'days[AM][1]': self.first_task.pk,
                                     'resource': response.context['resource'].pk,
                                     'start_date': '2016-03-07'})
        self.assertRedirects(response, '/schedule/')

        task = Task.objects.get(pk=self.first_task.pk)
        self.assertEquals(task.gain(), 0)
        self.assertEquals(task.days_worked, 1.5)

        response = self.client.get("/schedule/resource-weekly/view/worker")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["tasks"],
                         [self.first_task])

        response = self.client.post("/schedule/resource-weekly/update",
                                    {'days[AM][0]': self.first_task.pk,
                                     'days[PM][0]': self.first_task.pk,
                                     'days[AM][1]': self.first_task.pk,
                                     'resource': response.context['resource'].pk,
                                     'start_date': '2016-03-07'})
        self.assertRedirects(response, '/schedule/')

        task = Task.objects.get(pk=self.first_task.pk)
        self.assertEquals(task.gain(), 0)
        self.assertEquals(task.days_worked, 1.5)

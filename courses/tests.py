from django.test import TestCase
from django.urls import reverse

from .models import Course


class CourseCRUDTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            code="CS101", title="Intro to CS", credits=4, level="BEG"
        )

    def test_list_view(self):
        resp = self.client.get(reverse("courses:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "CS101")

    def test_detail_view(self):
        resp = self.client.get(reverse("courses:detail", args=[self.course.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Intro to CS")

    def test_create_view(self):
        resp = self.client.post(
            reverse("courses:create"),
            {
                "code": "MATH201",
                "title": "Calculus",
                "level": "INT",
                "credits": 3,
                "is_active": True,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Course.objects.filter(code="MATH201").exists())

    def test_update_view(self):
        resp = self.client.post(
            reverse("courses:update", args=[self.course.pk]),
            {
                "code": "CS101",
                "title": "Intro to Computer Science",
                "level": "BEG",
                "credits": 4,
                "is_active": True,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Intro to Computer Science")

    def test_delete_view(self):
        resp = self.client.post(reverse("courses:delete", args=[self.course.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

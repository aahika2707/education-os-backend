"""Transport endpoint tests: happy path + permission/validation cases.

The module's routes are not mounted in ``config/urls`` until the integrate step,
so these tests mount the router under a local ``ROOT_URLCONF`` for isolation.
"""
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import include, path, reverse
from rest_framework.test import APITestCase

from core.permissions import Role

from academics.models import Department, Program, Section, Semester
from students.models import Student

from transport.models import BusLiveStatus, BusRoute, BusStop

User = get_user_model()

# Mount the full transport URL surface (router + the {user_id} spec route).
urlpatterns = [path("", include("transport.urls"))]


@override_settings(ROOT_URLCONF=__name__)
class TransportAPITests(APITestCase):
    def setUp(self):
        pwd = "Str0ng-Pass!23"
        self.admin = User.objects.create_user(
            email="admin@example.com", password=pwd, full_name="Admin", role=Role.ADMIN
        )
        self.student = User.objects.create_user(
            email="abin@example.com", password=pwd, full_name="Abin", role=Role.STUDENT
        )
        self.other_student_user = User.objects.create_user(
            email="neha@example.com", password=pwd, full_name="Neha", role=Role.STUDENT
        )

        dept = Department.objects.create(code="CSE", name="Computer Science")
        program = Program.objects.create(
            code="BTCSE", name="B.Tech CSE", department=dept,
            duration_years=4, intake=60,
        )
        sem = Semester.objects.create(program=program, number=5)
        section = Section.objects.create(semester=sem, name="A")
        self.student_profile = Student.objects.create(
            user=self.student, roll_no="CSE-001", program=program,
            department=dept, semester=sem, section=section, full_name="Abin",
        )

        self.route = BusRoute.objects.create(
            name="City Center Loop", number="R1",
            driver="Suresh", driver_phone="+91-99999-00000",
        )
        BusStop.objects.create(route=self.route, name="Main Gate", time="08:00", order=1)
        BusStop.objects.create(route=self.route, name="Library", time="08:15", order=2)
        self.live = BusLiveStatus.objects.create(
            route=self.route, current_stop="Main Gate", next_stop="Library",
            eta_mins=7, occupancy=42, lat=10.5, lng=76.2,
        )

    # -- reads open to any authenticated role ----------------------------
    def test_list_routes_app_shape(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get(reverse("transport:busroute-list"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(len(data), 1)
        route = data[0]
        # App-shaped BusRoute: camelCase `driverPhone`, nested `stops`.
        self.assertEqual(route["number"], "R1")
        self.assertEqual(route["driverPhone"], "+91-99999-00000")
        self.assertEqual(len(route["stops"]), 2)
        self.assertEqual(route["stops"][0], {"name": "Main Gate", "time": "08:00"})

    def test_list_requires_auth(self):
        self.assertEqual(
            self.client.get(reverse("transport:busroute-list")).status_code, 401
        )

    def test_route_live_app_shape(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get(
            reverse("transport:busroute-live", args=[self.route.id])
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        # App-shaped BusLiveStatus: camelCase keys, routeId string.
        self.assertEqual(data["routeId"], str(self.route.id))
        self.assertEqual(data["currentStop"], "Main Gate")
        self.assertEqual(data["nextStop"], "Library")
        self.assertEqual(data["etaMins"], 7)
        self.assertEqual(data["occupancy"], 42)

    def test_route_live_404_when_absent(self):
        route2 = BusRoute.objects.create(name="No Live", number="R2")
        self.client.force_authenticate(self.student)
        resp = self.client.get(reverse("transport:busroute-live", args=[route2.id]))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["status"], "error")

    # -- write RBAC ------------------------------------------------------
    def test_student_cannot_create_route(self):
        self.client.force_authenticate(self.student)
        resp = self.client.post(
            reverse("transport:busroute-list"),
            {"name": "New", "number": "R9"}, format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_route_and_it_is_audited(self):
        from core.models import AuditLog

        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            reverse("transport:busroute-list"),
            {"name": "New Route", "number": "R9", "driver": "Ravi",
             "driver_phone": "+91-88888-00000"}, format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(BusRoute.objects.filter(number="R9").exists())
        self.assertTrue(
            AuditLog.objects.filter(entity="BusRoute", action="create").exists()
        )

    def test_create_route_validation_error(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            reverse("transport:busroute-list"),
            {"name": "Missing Number"}, format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["status"], "error")

    # -- mobile API contract v1: GET /transport/{user_id} ----------------
    def test_transport_by_user_spec_shape(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get(
            reverse("transport:transport-by-user", args=[self.student.id])
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["route"], "City Center Loop")
        self.assertEqual(data["driver"], "Suresh")
        self.assertEqual(data["phone"], "+91-99999-00000")
        self.assertEqual(data["live_location"], {"lat": 10.5, "lng": 76.2})
        self.assertEqual(data["eta"], 7)
        self.assertEqual(data["occupancy"], 42)
        self.assertEqual(data["stops"][0], {"name": "Main Gate", "time": "08:00"})

    def test_transport_by_user_denies_other_user(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get(
            reverse("transport:transport-by-user", args=[self.other_student_user.id])
        )
        self.assertEqual(resp.status_code, 403)

    def test_transport_by_user_staff_any(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get(
            reverse("transport:transport-by-user", args=[self.student.id])
        )
        self.assertEqual(resp.status_code, 200)

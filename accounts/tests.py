"""Auth endpoint tests: happy path + auth/permission + validation failures."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import OTP
from core.permissions import Role

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.password = "Str0ng-Pass!23"
        self.user = User.objects.create_user(
            email="abin@example.com",
            password=self.password,
            full_name="Abin Thomas",
            role=Role.STUDENT,
        )

    # -- login ------------------------------------------------------------
    def test_login_returns_user_access_refresh_and_token(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"email": self.user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "success")
        data = body["data"]
        # Spec-exact fields.
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["active_role"], Role.STUDENT)
        # Legacy aliases retained for back-compat.
        self.assertEqual(data["access"], data["access_token"])
        self.assertEqual(data["refresh"], data["refresh_token"])
        self.assertEqual(data["token"], data["access"])  # mobile alias
        self.assertEqual(data["user"]["email"], self.user.email)
        self.assertEqual(data["user"]["name"], "Abin Thomas")
        self.assertEqual(data["user"]["avatarColor"][0], "#")

    def test_login_with_phone_credential(self):
        self.user.phone = "9998887777"
        self.user.save(update_fields=["phone"])
        resp = self.client.post(
            reverse("accounts:login"),
            {"phone": self.user.phone, "password": self.password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["user"]["email"], self.user.email)

    def test_login_bad_password_is_401_enveloped(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"email": self.user.email, "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)
        body = resp.json()
        self.assertEqual(body["status"], "error")
        self.assertTrue(body["errors"])

    def test_login_validation_error_is_400(self):
        resp = self.client.post(reverse("accounts:login"), {"email": "x"}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["status"], "error")

    # -- me ---------------------------------------------------------------
    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse("accounts:me")).status_code, 401)

    def test_me_returns_current_user(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse("accounts:me"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["email"], self.user.email)

    # -- roles / switch-role ---------------------------------------------
    def test_roles_returns_user_roles(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse("accounts:roles", args=[self.user.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["roles"], [Role.STUDENT])

    def test_roles_student_cannot_read_other_user(self):
        other = User.objects.create_user(
            email="other@example.com", password=self.password, full_name="Other", role=Role.STUDENT
        )
        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse("accounts:roles", args=[other.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_roles_staff_can_read_any_user(self):
        staff = User.objects.create_user(
            email="hod@example.com", password=self.password, full_name="HOD", role=Role.HOD
        )
        self.client.force_authenticate(staff)
        resp = self.client.get(reverse("accounts:roles", args=[self.user.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_switch_role_to_own_role_reissues_token(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("accounts:switch-role"), {"role": Role.STUDENT}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertIn("access_token", data)
        self.assertEqual(data["active_role"], Role.STUDENT)

    def test_switch_role_to_foreign_role_is_403(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("accounts:switch-role"), {"role": Role.ADMIN}, format="json"
        )
        self.assertEqual(resp.status_code, 403)

    # -- register (admin only) -------------------------------------------
    def test_register_forbidden_for_student(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("accounts:register"),
            {"email": "new@example.com", "full_name": "New", "role": Role.FACULTY, "password": "Str0ng-Pass!23"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_register_allowed_for_admin(self):
        admin = User.objects.create_user(
            email="admin@example.com", password=self.password, full_name="Admin", role=Role.ADMIN
        )
        self.client.force_authenticate(admin)
        resp = self.client.post(
            reverse("accounts:register"),
            {"email": "new@example.com", "full_name": "New Faculty", "role": Role.FACULTY, "password": "Str0ng-Pass!23"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    # -- password reset ---------------------------------------------------
    def test_forgot_password_always_200(self):
        resp = self.client.post(
            reverse("accounts:forgot-password"), {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(resp.status_code, 200)

    def test_reset_password_with_valid_otp(self):
        otp = OTP.issue(self.user, purpose=OTP.PURPOSE_RESET)
        resp = self.client.post(
            reverse("accounts:reset-password"),
            {"email": self.user.email, "code": otp.code, "new_password": "N3w-Pass!word"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("N3w-Pass!word"))

    def test_reset_password_bad_otp_is_400(self):
        resp = self.client.post(
            reverse("accounts:reset-password"),
            {"email": self.user.email, "code": "000000", "new_password": "N3w-Pass!word"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # -- change password --------------------------------------------------
    def test_change_password(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("accounts:change-password"),
            {"current_password": self.password, "new_password": "N3w-Pass!word"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("N3w-Pass!word"))

    # -- logout -----------------------------------------------------------
    def test_logout_blacklists_refresh(self):
        login = self.client.post(
            reverse("accounts:login"),
            {"email": self.user.email, "password": self.password},
            format="json",
        ).json()["data"]
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("accounts:logout"), {"refresh": login["refresh"]}, format="json"
        )
        self.assertEqual(resp.status_code, 200)

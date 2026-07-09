"""I/O serializers for the academics app.

Two flavours:

* CRUD serializers (``*Serializer``) — used by the admin/HOD management viewsets.
  They accept/return the model fields plus FK ids.
* App-shaped serializers (``SubjectAppSerializer`` / ``ClassSessionAppSerializer``)
  — emit the exact camelCase shapes the mobile app expects (``types.ts``:
  ``Subject`` and ``ClassSession``) for the timetable / subject-detail endpoints.
"""
from rest_framework import serializers

from academics.models import (
    ClassSession,
    Department,
    Program,
    Section,
    Semester,
    Subject,
)


# --- CRUD serializers --------------------------------------------------------
class DepartmentSerializer(serializers.ModelSerializer):
    hod_name = serializers.CharField(source="hod.full_name", read_only=True, default=None)

    class Meta:
        model = Department
        fields = ["id", "code", "name", "hod", "hod_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProgramSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(
        source="department.code", read_only=True
    )
    department_name = serializers.CharField(
        source="department.name", read_only=True
    )

    class Meta:
        model = Program
        fields = [
            "id",
            "code",
            "name",
            "department",
            "department_code",
            "department_name",
            "duration_years",
            "intake",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SemesterSerializer(serializers.ModelSerializer):
    program_code = serializers.CharField(source="program.code", read_only=True)

    class Meta:
        model = Semester
        fields = ["id", "program", "program_code", "number", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "semester", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(
        source="department.code", read_only=True
    )
    semester_number = serializers.IntegerField(
        source="semester.number", read_only=True, default=None
    )
    program_code = serializers.CharField(
        source="semester.program.code", read_only=True, default=None
    )
    faculty_email = serializers.EmailField(
        source="faculty.email", read_only=True, default=None
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "credits",
            "department",
            "department_code",
            "semester",
            "semester_number",
            "program_code",
            "faculty",
            "faculty_name",
            "faculty_email",
            "color",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "faculty_name", "created_at", "updated_at"]


class ClassSessionSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.full_name", read_only=True, default=None)

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "subject",
            "section",
            "faculty",
            "faculty_name",
            "day",
            "start",
            "end",
            "room",
            "type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# --- App-shaped read serializers (mobile contract) ---------------------------
class SubjectAppSerializer(serializers.ModelSerializer):
    """Matches ``types.ts`` ``Subject`` shape (camelCase, ``faculty`` string)."""

    id = serializers.CharField(read_only=True)
    faculty = serializers.CharField(source="faculty_name", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "code", "name", "credits", "faculty", "color"]


class ClassSessionAppSerializer(serializers.ModelSerializer):
    """Matches ``types.ts`` ``ClassSession`` shape (camelCase, ``subjectId``)."""

    id = serializers.CharField(read_only=True)
    subjectId = serializers.CharField(source="subject_id", read_only=True)

    class Meta:
        model = ClassSession
        fields = ["id", "subjectId", "day", "start", "end", "room", "type"]


# --- Mobile API contract v1 (spec-exact, snake_case) -------------------------
class AcademicRecordSerializer(serializers.Serializer):
    """Spec-exact shape for ``GET /api/v1/academics/{user_id}``.

    ``API_CONTRACT_V1`` §Academics:
    ``{ degree, department, semester, section, mentor, cgpa }``.
    """

    degree = serializers.CharField(allow_blank=True)
    department = serializers.CharField(allow_blank=True)
    semester = serializers.IntegerField()
    section = serializers.CharField(allow_blank=True)
    mentor = serializers.CharField(allow_blank=True)
    cgpa = serializers.FloatField()


class GpaTrendPointSerializer(serializers.Serializer):
    """One ``{ semester, gpa }`` point of the academic-progress GPA trend."""

    semester = serializers.CharField()
    gpa = serializers.FloatField()


class AcademicProgressSerializer(serializers.Serializer):
    """Spec-exact shape for ``GET /api/v1/progress/{user_id}``.

    ``API_CONTRACT_V1`` §Academic Progress:
    ``{ gpa_trend:[{semester,gpa}], semester_gpa, overall_cgpa, ai_insights:[...] }``.
    """

    gpa_trend = GpaTrendPointSerializer(many=True)
    semester_gpa = serializers.FloatField()
    overall_cgpa = serializers.FloatField()
    ai_insights = serializers.ListField(child=serializers.DictField())

"""Campus URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so the router
paths resolve to ``/api/v1/campus/locations`` and
``/api/v1/campus/locations/{id}``.
"""
from rest_framework.routers import DefaultRouter

from campus.views import CampusLocationViewSet

app_name = "campus"

router = DefaultRouter(trailing_slash=False)
router.register("campus/locations", CampusLocationViewSet, basename="campus-location")

urlpatterns = router.urls

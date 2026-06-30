from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CourseForm
from .models import Course


class CourseListView(ListView):
    model = Course
    paginate_by = 20


class CourseDetailView(DetailView):
    model = Course


class CourseCreateView(SuccessMessageMixin, CreateView):
    model = Course
    form_class = CourseForm
    success_message = "Course %(code)s was created."


class CourseUpdateView(SuccessMessageMixin, UpdateView):
    model = Course
    form_class = CourseForm
    success_message = "Course %(code)s was updated."


class CourseDeleteView(SuccessMessageMixin, DeleteView):
    model = Course
    success_url = reverse_lazy("courses:list")
    success_message = "Course was deleted."

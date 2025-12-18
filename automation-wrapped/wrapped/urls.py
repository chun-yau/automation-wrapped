from django.urls import path

from . import views

urlpatterns = [
    path("", views.wrapped, name="wrapped"),
]
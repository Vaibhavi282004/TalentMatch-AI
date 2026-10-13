from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("new/", views.home, name="home"),
    path("results/<int:pk>/", views.results, name="results"),
    path("results/<int:pk>/csv/", views.export_csv, name="export_csv"),
    path("results/<int:pk>/delete/", views.delete_screening, name="delete_screening"),
    path("history/", views.history, name="history"),
]

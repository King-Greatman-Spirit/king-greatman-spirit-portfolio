from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('project/<slug:project_slug>/', views.project_detail, name='project_detail'),
    path('service/<slug:service_slug>/service/', views.service_projects, name='service_projects'),
    path('projects/all/', views.all_projects, name='all_projects'),
]

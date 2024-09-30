from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('basic', views.submission_basic, name='basic'),
    path('advanced', views.submission_advanced, name='advanced'),
    path('challenge', views.submission_challenge, name='challenge'),
    path('detail/<uuid:uid>', views.detail, name='detail'),
    path('status/<uuid:uid>', views.status, name='status'),
    path('download/<uuid:uid>', views.results, name='results'),
    path('delete/<uuid:uid>', views.delete, name='delete'),
]
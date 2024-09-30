from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('overview', views.overview, name='overview'),
    path('detail/<uuid:uid>', views.detail, name='detail'),
]
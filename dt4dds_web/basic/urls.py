from django.urls import path
from . import views

app_name = 'basic'

urlpatterns = [
    path('', views.index, name='home'),
    path('imprint', views.imprint, name='imprint'),
    path('about', views.about, name='about'),
    path('challenge', views.challenge, name='challenge'),
]
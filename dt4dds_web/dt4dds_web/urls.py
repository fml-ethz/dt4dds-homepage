from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

admin.site.site_header = "DT4DDS Web Server"
admin.site.site_title = "DT4DDS Web Server - Admin Portal"
admin.site.index_title = "Welcome to DT4DDS Web Server"

urlpatterns = [
    path('', include('basic.urls', namespace='basic')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('leaderboard/', include('leaderboard.urls', namespace='leaderboard')),
    path('admin/', admin.site.urls),
]


def error(request, exception=None):
    return render(request, 'error.html', context={'title': "Something went wrong ..."})

handler404 = error
handler500 = error
handler403 = error
handler400 = error


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
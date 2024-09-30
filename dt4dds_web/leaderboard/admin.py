from django.contrib import admin

from .models import Leaderboard, Entry


admin.site.register(Leaderboard)
admin.site.register(Entry)
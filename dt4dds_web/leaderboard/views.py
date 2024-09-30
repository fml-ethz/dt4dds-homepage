import logging
from django.shortcuts import render
from .models import Entry, Leaderboard

logger = logging.getLogger("dt4dds_web.leaderboard.views")




def overview(request):

    leaderboard_decay = Leaderboard.objects.get(slug='decay')
    leaderboard_photolithography = Leaderboard.objects.get(slug='photolithography')

    context = {
        'title': 'Challenge Leaderboard',
        'meta_title': 'Leaderboard',
        'leaderboard_decay': leaderboard_decay.entries.all().order_by('-code_rate'),
        'leaderboard_photolithography': leaderboard_photolithography.entries.all().order_by('-code_rate'),
    }

    return render(request, 'leaderboard/overview.html', context=context)


def detail(request, uid):

    entry = Entry.objects.get(pk=uid)
    leaderboard = entry.leaderboard
    position = Entry.objects.filter(leaderboard=leaderboard, code_rate__gt=entry.code_rate).count() + 1

    context = {
        'title': 'Submission details',
        'meta_title': 'Details',
        'id': uid,
        'entry': entry,
        'leaderboard': leaderboard,
        'position': position,
    }

    return render(request, 'leaderboard/detail.html', context=context)

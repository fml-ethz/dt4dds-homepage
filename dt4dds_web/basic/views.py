import logging
from django.shortcuts import render

logger = logging.getLogger("dt4dds_web.basic.views")

def index(request):

    context = {
        'title': '<strong>DT4DDS</strong><br>Digital Twin for DNA Data Storage',
        'meta_title': 'Home'
    }
 
    return render(request, 'basic/home.html', context=context)


def imprint(request):

    context = {
        'title': 'Imprint',
        'meta_title': 'Imprint'
    }

    return render(request, 'basic/imprint.html', context=context)


def about(request):

    context = {
        'title': 'About DT4DDS',
        'meta_title': 'About'
    }

    return render(request, 'basic/about.html', context=context)


def challenge(request):

    context = {
        'title': 'About the DT4DDS-Challenges',
        'meta_title': 'Challenges'
    }

    return render(request, 'basic/challenge.html', context=context)
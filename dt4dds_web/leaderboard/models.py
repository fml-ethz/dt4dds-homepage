from django.db import models

import logging
logger = logging.getLogger("dt4dds_web.leaderboard.models")

import uuid



class Leaderboard(models.Model):

    name = models.CharField("Leaderboard name", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True, primary_key=True)
    description = models.TextField("Description", default="")
    is_active = models.BooleanField("Is active?", default=True)



class Entry(models.Model):

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_date = models.DateTimeField('Submission date', auto_now_add=True)
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')

    name = models.CharField('Name', max_length=200)
    authors = models.CharField('Authors', max_length=200)
    code_rate = models.FloatField('Code rate')
    doi = models.CharField('DOI', max_length=200, default="")
    repository = models.CharField('Repository', max_length=200, default="")
    description = models.TextField('Description', default="")

    is_verified = models.BooleanField('Is verified?', default=False)


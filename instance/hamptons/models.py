
from datetime import datetime
from hamptons.conf import settings
from hamptons.utils import RedisHash

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify

import autoslug



class Hamptonian(AbstractUser):
    
    def __init__(self, *args, **kwargs):
        super(Hamptonian, self).__init__(*args, **kwargs)
        if self.username
    
    @property
    def stash(self):
        """ Access to a per-user Redis hash """
        return RedisHash
    
    @property
    def signing_key(self):
        """ Get a salted SHA1 nonce of the user oAuth key """

class Frampton(models.Model):
    """ A Frampton session """
    
    class Meta:
        verbose_name = "Frampton"
        verbose_name_plural = "Frampton Sessions"
        abstract = False
    
    createdate = models.DateTimeField('Created on',
        default=datetime.now,
        auto_now_add=True,
        blank=True,
        editable=False)
    
    modifydate = models.DateTimeField('Last modified on',
        default=datetime.now,
        auto_now=True,
        blank=True,
        editable=False)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name="framptons",
        verbose_name="Creator",
        editable=True)
    
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
        related_name='participating_in',
        verbose_name="Participants",
        editable=True)
    
    title = models.CharField(verbose_name="FFFFound Title",
        max_length=255,
        db_index=True,
        unique=False,
        blank=True,
        null=True)
    
    slug = autoslug.AutoSlugField(
        populate_from=lambda instance: instance.title,
        slugify=slugify,
        db_index=True,
        blank=True,
        editable=True)
    
    state = models.PositiveSmallIntegerField(
        verbose_name="State",
        null=False,
        blank=False,
        choices=(
            (0, 'Created'),
            (1, 'Ready'),
            (2, 'IN PROGRESS'),
            (3, 'Done'),
        ))
    

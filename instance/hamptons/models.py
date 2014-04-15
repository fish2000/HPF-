
from hashlib import sha256
from datetime import datetime
from hamptons.conf import settings
from sandpiper.structs import RedisDict
from sandpiper.redpool import redpool as redis

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify

import autoslug
from durationfield.db.models.fields import duration

class Hamptonian(AbstractUser):
    
    def __init__(self, *args, **kwargs):
        super(Hamptonian, self).__init__(*args, **kwargs)
        if self.username:
            self._stash = RedisDict(self.username, redis)
    
    @property
    def name(self):
        return self.get_full_name() or self.username
    
    @property
    def social(self):
        try:
            return self.socialaccount_set.get()
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            # TOO MANY MCs NOT ENOUGH TWITS
            pass
        raise ValueError("User %s has too much social" % self.username)
    
    @property
    def provider(self):
        return self.social.get_provider()
    
    @property
    def extra_data(self):
        return self.social.extra_data
    
    @property
    def at_name(self):
        return self.extra_data.get('screen_name', None)
    
    @property
    def tokens(self):
        return self.social.socialtoken_set.all()
    
    @property
    def app(self):
        # this may change (it probably should, OMG SHHHH
        # THE SOFTWARE ARCHITECT WILL HEAR YOU DOGG)
        return list(self.tokens).pop().app
    
    @property
    def credentials(self):
        """ See twitter.oauth_doc and twemoir.models.__doc__
            if you want something that can pass as an explanation
            for oauth's comprehensively nonsensical weird quirks
            e.g. THE INCONSISTENTLY CAPITALIZED DICTIONARY KEYS
            YOU SEE BELOW WHICH WERE NOT MY FREAKING IDEA AT ALL.
        """
        token = list(self.tokens).pop() # for now
        return dict(
            oauth_token=token.app.client_id,
            oauth_token_secret=token.app.secret,
            CONSUMER_KEY=token.token,
            CONSUMER_SECRET=token.token_secret)
    
    @property
    def avatar_url(self):
        return self.social.get_avatar_url()
    
    @property
    def stash(self):
        """ Access to a per-user Redis hash """
        if hasattr(self, '_stash'):
            return self._stash
        if self.username:
            self._stash = RedisDict(self.username, redis)
            return self._stash
        raise ValueError('Redis stash uninitialized!')
    
    @property
    def signing_key(self):
        """ Get a salted SHA1 nonce of the user oAuth key """
        if 'signing_key' not in self.stash:
            token_secret = list(self.tokens).pop().token_secret
            self.stash['signing_key'] = sha256(
                settings.HAMPTONS_SIGNING_SALT +
                token_secret).hexdigest()
        return self.stash['signing_key']
    

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
    
    startdate = models.DateTimeField('Start Date/Time',
        blank=True,
        null=True,
        editable=True)
    
    length = duration.DurationField('Length in Time',
        blank=True,
        null=True,
        editable=True)


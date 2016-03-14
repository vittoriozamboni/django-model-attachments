from __future__ import unicode_literals

import os

from django.conf import settings as dj_settings
from django.db import models


ATTACHMENT_TYPES = (
    ('file', 'File'),
    ('url', 'URL'),
)


class AuditLogMixin(models.Model):
    """
    Add these fields to your model:

    from AuditLogMixin:
    :parameter: creation_date
    :parameter: created_by
    :parameter: last_edit_date
    :parameter: last_edit_by
    :parameter: audit_user (used to automatically set created_by and last_edit_by)
    """

    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(getattr(dj_settings, 'AUTH_USER_MODEL', 'auth.User'),
                                   related_name="created_%(app_label)s_%(class)s_set",
                                   null=True, blank=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    last_edit_by = models.ForeignKey(getattr(dj_settings, 'AUTH_USER_MODEL', 'auth.User'),
                                     related_name="edited_%(app_label)s_%(class)s_set",
                                     null=True, blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(AuditLogMixin, self).__init__(*args, **kwargs)
        self.audit_user = None

    def save(self, *args, **kwargs):
        if self.audit_user:
            if not self.creation_date:
                self.created_by = self.audit_user
            self.last_edit_by = self.audit_user
        super(AuditLogMixin, self).save(*args, **kwargs)

    def auditlog_register_creation(self, user):
        self.created_by = user
        self.last_edit_by = user

    def auditlog_register_edit(self, user):
        self.last_edit_by = user


class AttachmentMixin(AuditLogMixin):
    name = models.CharField(max_length=255)
    path = models.TextField()
    media_root = models.CharField(max_length=255, default='', blank=True)
    media_url = models.CharField(max_length=255, default='', blank=True)
    file_type = models.CharField(max_length=255, default='', blank=True)
    file_size = models.IntegerField(default=0)
    description = models.TextField(default='', blank=True)
    attachment_type = models.CharField(max_length=50, choices=ATTACHMENT_TYPES, default='file', blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{name}'.format(name=self.name)

    def __unicode__(self):
        return u'{name}'.format(name=self.name)

    @property
    def url(self):
        if self.media_url:
            return '/'.join([self.media_url, self.path]).replace('//', '/')
        else:
            return '/'.join([dj_settings.MEDIA_URL, self.path]).replace('//', '/')

    def delete(self, *args, **kwargs):
        if self.attachment_type == 'file':
            media_root = self.media_root
            if not self.media_path:
                media_root = dj_settings.MEDIA_ROOT
            os.remove(os.path.join(media_root, self.path))
        super(AttachmentMixin, self).delete(*args, **kwargs)

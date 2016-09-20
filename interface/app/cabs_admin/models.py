# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Blacklist(models.Model):
    address = models.CharField(primary_key=True, max_length=32, blank=True)
    banned = models.NullBooleanField(blank=True, null=True)
    attempts = models.NullBooleanField(blank=True, null=True)
    timecleared = models.TimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.pk
   
    class Meta:
        managed = False
        db_table = 'blacklist'


class Current(models.Model):
    user = models.CharField(max_length=32)
    name = models.CharField(max_length=32, blank=True)
    machine = models.CharField(primary_key=True, unique=True, max_length=32)
    confirmed = models.BooleanField(default=True)
    connecttime = models.DateTimeField()

    def __unicode__(self):
        return self.pk
   
    class Meta:
        managed = False
        db_table = 'current'


class Log(models.Model):
    timestamp = models.DateTimeField()
    msg_type = models.CharField(max_length=16, blank=True)
    message = models.CharField(max_length=1024, blank=True)
    id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'log'


class Machines(models.Model):
    name = models.CharField(max_length=32)
    machine = models.CharField(primary_key=True, unique=True, max_length=32)
    active = models.BooleanField(default=False)
    status = models.CharField(max_length=18, blank=True)
    last_heartbeat = models.DateTimeField()
    deactivated = models.BooleanField(default=False)
    reason = models.CharField(max_length=120, blank=True)
    
    def __unicode__(self):
        return self.pk
   
    class Meta:
        managed = False
        db_table = 'machines'


class Pools(models.Model):
    name = models.CharField(primary_key=True, max_length=32)
    description = models.CharField(max_length=1024, blank=True)
    secondary = models.CharField(max_length=1024, blank=True)
    groups = models.CharField(max_length=1024, blank=True)
    deactivated = models.BooleanField(default=False)
    reason = models.CharField(max_length=120, blank=True)

    def __unicode__(self):
        return self.pk
   
    class Meta:
        managed = False
        db_table = 'pools'

class Settings(models.Model):
    setting = models.CharField(primary_key=True, unique=True, max_length=32)
    value = models.CharField(max_length=64)
    applied = models.NullBooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'settings'

class Whitelist(models.Model):
    address = models.CharField(primary_key=True, unique=True, max_length=32)

    def __unicode__(self):
        return self.pk
   
    class Meta:
        managed = False
        db_table = 'whitelist'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blacklist',
            fields=[
                ('address', models.CharField(max_length=32, serialize=False, primary_key=True, blank=True)),
                ('banned', models.NullBooleanField()),
                ('attempts', models.NullBooleanField()),
                ('timecleared', models.TimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'blacklist',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Current',
            fields=[
                ('user', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=32, blank=True)),
                ('machine', models.CharField(max_length=32, unique=True, serialize=False, primary_key=True)),
                ('confirmed', models.BooleanField(default=True)),
                ('connecttime', models.DateTimeField()),
            ],
            options={
                'db_table': 'current',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('timestamp', models.DateTimeField()),
                ('msg_type', models.CharField(max_length=16, blank=True)),
                ('message', models.CharField(max_length=1024, blank=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'log',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Machines',
            fields=[
                ('name', models.CharField(max_length=32)),
                ('machine', models.CharField(max_length=32, unique=True, serialize=False, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=18)),
                ('last_heartbeat', models.DateTimeField()),
                ('deactivated', models.BooleanField(default=False)),
                ('reason', models.CharField(max_length=120, blank=True)),
            ],
            options={
                'db_table': 'machines',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pools',
            fields=[
                ('name', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=1024, blank=True)),
                ('secondary', models.CharField(max_length=1024, blank=True)),
                ('groups', models.CharField(max_length=1024, blank=True)),
                ('deactivated', models.BooleanField(default=False)),
                ('reason', models.CharField(max_length=120, blank=True)),
            ],
            options={
                'db_table': 'pools',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('setting', models.CharField(max_length=32, unique=True, serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'settings',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Whitelist',
            fields=[
                ('address', models.CharField(max_length=32, unique=True, serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'whitelist',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]

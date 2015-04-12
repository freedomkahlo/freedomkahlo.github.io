# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_auto_20150412_0032'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posstime',
            old_name='votes',
            new_name='nConflicts',
        ),
        migrations.RemoveField(
            model_name='posstime',
            name='time',
        ),
        migrations.AddField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 12, 5, 56, 56, 796000), verbose_name=b'end time'),
        ),
        migrations.AddField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 12, 5, 56, 56, 796000), verbose_name=b'start time'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='end_date',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='instance',
            name='start_date',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(related_name='UserProfile', to=settings.AUTH_USER_MODEL),
        ),
    ]

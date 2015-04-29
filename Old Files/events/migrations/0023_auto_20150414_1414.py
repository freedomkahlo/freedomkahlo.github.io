# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0022_auto_20150412_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='activation_key',
            field=models.CharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 14, 14, 14, 51, 394000), verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 14, 14, 14, 51, 394000), verbose_name=b'start time'),
        ),
    ]

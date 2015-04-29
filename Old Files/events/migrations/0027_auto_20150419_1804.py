# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_auto_20150419_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='firstName',
            field=models.CharField(default=b'', max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='lastName',
            field=models.CharField(default=b'', max_length=30),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 4, 39, 611433), verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 4, 39, 611397), verbose_name=b'start time'),
        ),
    ]

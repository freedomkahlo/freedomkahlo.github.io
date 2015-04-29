# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0023_auto_20150414_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='time_length',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='instance',
            name='end_date',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='instance',
            name='end_time',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='instance',
            name='start_date',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='instance',
            name='start_time',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 17, 10, 47, 28, 900000), verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 17, 10, 47, 28, 900000), verbose_name=b'start time'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_auto_20150419_1818'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='firstName',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='lastName',
        ),
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 22, 19, 108043), verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 22, 19, 108012), verbose_name=b'start time'),
        ),
    ]

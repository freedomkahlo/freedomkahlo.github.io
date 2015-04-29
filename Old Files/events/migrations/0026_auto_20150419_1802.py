# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0025_auto_20150417_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 2, 21, 828930), verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 19, 18, 2, 21, 828897), verbose_name=b'start time'),
        ),
    ]

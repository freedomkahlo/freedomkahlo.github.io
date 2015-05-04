# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150504_0337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='scheduled_end',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 4, 7, 37, 9, 233000, tzinfo=utc), verbose_name=b'event time2'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='scheduled_start',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 4, 7, 37, 9, 233000, tzinfo=utc), verbose_name=b'event time'),
        ),
    ]

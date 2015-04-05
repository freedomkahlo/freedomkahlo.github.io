# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20150405_0428'),
    ]

    operations = [
        migrations.AddField(
            model_name='desc',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 5, 8, 51, 49, 236070, tzinfo=utc), verbose_name='date made'),
        ),
    ]

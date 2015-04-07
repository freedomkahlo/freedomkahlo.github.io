# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_desc_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desc',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date made', default=datetime.datetime(2015, 4, 5, 8, 52, 33, 501601, tzinfo=utc)),
        ),
    ]

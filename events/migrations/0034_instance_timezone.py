# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_auto_20150501_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='timezone',
            field=models.CharField(default=b'Eastern', max_length=20),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_auto_20150422_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='eventID',
            field=models.CharField(default=b'', max_length=32),
        ),
    ]

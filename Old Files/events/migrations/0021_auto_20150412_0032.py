# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_auto_20150412_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='refToken',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20150406_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='creator',
            field=models.CharField(default='', max_length=100),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_potentialtimes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potentialtimes',
            name='event',
        ),
        migrations.AddField(
            model_name='instance',
            name='is_scheduled',
            field=models.BooleanField(default='False'),
        ),
        migrations.DeleteModel(
            name='PotentialTimes',
        ),
    ]

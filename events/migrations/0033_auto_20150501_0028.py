# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_instance_eventid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posstime',
            old_name='nConflicts',
            new_name='nFree',
        ),
        migrations.AddField(
            model_name='posstime',
            name='peopleList',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]

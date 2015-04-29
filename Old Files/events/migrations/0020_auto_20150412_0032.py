# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='gcalEmail',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='refToken',
            field=models.CharField(default='hello', max_length=100),
            preserve_default=False,
        ),
    ]

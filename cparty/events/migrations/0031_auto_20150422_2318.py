# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitee',
            name='rsvpAccepted',
        ),
        migrations.RemoveField(
            model_name='invitee',
            name='userID',
        ),
        migrations.AlterField(
            model_name='posstime',
            name='endTime',
            field=models.DateTimeField(verbose_name=b'end time'),
        ),
        migrations.AlterField(
            model_name='posstime',
            name='startTime',
            field=models.DateTimeField(verbose_name=b'start time'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posstime',
            old_name='nConflicts',
            new_name='nFree',
        ),
        migrations.RemoveField(
            model_name='invitee',
            name='rsvpAccepted',
        ),
        migrations.RemoveField(
            model_name='invitee',
            name='userID',
        ),
        migrations.AddField(
            model_name='posstime',
            name='peopleList',
            field=models.CharField(default=b'', max_length=100),
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

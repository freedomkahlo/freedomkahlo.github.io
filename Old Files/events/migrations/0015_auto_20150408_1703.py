# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20150408_1657'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rsvpinvitee',
            name='event',
        ),
        migrations.AddField(
            model_name='invitee',
            name='rsvpStatus',
            field=models.BooleanField(default='False'),
        ),
        migrations.DeleteModel(
            name='RsvpInvitee',
        ),
    ]

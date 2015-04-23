# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20150408_1703'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitee',
            old_name='rsvpStatus',
            new_name='rsvpAccepted',
        ),
    ]

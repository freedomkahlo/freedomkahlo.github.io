# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20150408_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='rsvpAccepted',
            field=models.BooleanField(default=None),
        ),
    ]

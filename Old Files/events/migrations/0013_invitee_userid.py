# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20150408_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitee',
            name='userID',
            field=models.IntegerField(default='0'),
        ),
    ]

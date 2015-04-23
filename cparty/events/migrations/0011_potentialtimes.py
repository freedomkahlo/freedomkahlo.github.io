# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_rsvplist'),
    ]

    operations = [
        migrations.CreateModel(
            name='PotentialTimes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('time', models.DateTimeField(verbose_name='potential time')),
                ('votes', models.IntegerField(default=0)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
    ]

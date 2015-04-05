# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_initialrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='InitTimes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('start_time', models.TimeField(verbose_name='start time')),
                ('end_time', models.TimeField(verbose_name='end time')),
                ('event', models.ForeignKey(to='events.Desc')),
            ],
        ),
        migrations.DeleteModel(
            name='InitialRequest',
        ),
    ]

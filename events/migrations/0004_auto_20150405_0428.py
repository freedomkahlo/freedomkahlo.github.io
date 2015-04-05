# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20150405_0400'),
    ]

    operations = [
        migrations.CreateModel(
            name='InitTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('start_time', models.TimeField(verbose_name='start time')),
                ('end_time', models.TimeField(verbose_name='end time')),
                ('event', models.ForeignKey(to='events.Desc')),
            ],
        ),
        migrations.RemoveField(
            model_name='inittimes',
            name='event',
        ),
        migrations.DeleteModel(
            name='InitTimes',
        ),
    ]

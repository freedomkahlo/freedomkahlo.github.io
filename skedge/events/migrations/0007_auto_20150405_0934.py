# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20150405_0452'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=20)),
                ('desc', models.CharField(default='description', max_length=100)),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2015, 4, 5, 13, 34, 23, 836114, tzinfo=utc), verbose_name='date made')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('start_time', models.TimeField(verbose_name='start time')),
                ('end_time', models.TimeField(verbose_name='end time')),
            ],
        ),
        migrations.RemoveField(
            model_name='inittime',
            name='event',
        ),
        migrations.AlterField(
            model_name='invitee',
            name='event',
            field=models.ForeignKey(to='events.Instance'),
        ),
        migrations.DeleteModel(
            name='Desc',
        ),
        migrations.DeleteModel(
            name='InitTime',
        ),
    ]

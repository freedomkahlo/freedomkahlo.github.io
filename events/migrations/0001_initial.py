# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=20)),
                ('desc', models.CharField(default=b'description', max_length=100)),
                ('pub_date', models.DateTimeField(verbose_name=b'date made')),
                ('start_date', models.CharField(default=b'', max_length=20)),
                ('end_date', models.CharField(default=b'', max_length=20)),
                ('start_time', models.CharField(default=b'', max_length=20)),
                ('end_time', models.CharField(default=b'', max_length=20)),
                ('event_length', models.CharField(default=b'', max_length=20)),
                ('creator', models.CharField(default=b'', max_length=100)),
                ('eventID', models.CharField(default=b'', max_length=32)),
                ('timezone', models.CharField(default=b'Eastern', max_length=20)),
                ('is_scheduled', models.BooleanField(default=False)),
                ('scheduled_start', models.DateTimeField(default=datetime.datetime(2015, 5, 4, 7, 36, 59, 990000, tzinfo=utc), verbose_name=b'event time')),
                ('scheduled_end', models.DateTimeField(default=datetime.datetime(2015, 5, 4, 7, 36, 59, 990000, tzinfo=utc), verbose_name=b'event time2')),
            ],
        ),
        migrations.CreateModel(
            name='Invitee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('firstName', models.CharField(default=b'', max_length=100)),
                ('lastName', models.CharField(default=b'', max_length=100)),
                ('hasVoted', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(default=b'', max_length=200)),
                ('author', models.CharField(default=b'', max_length=100)),
                ('firstName', models.CharField(default=b'', max_length=100)),
                ('lastName', models.CharField(default=b'', max_length=100)),
                ('pub_date', models.DateTimeField(verbose_name=b'date made')),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notificationType', models.CharField(default=b'', max_length=50)),
                ('originUserName', models.CharField(default=b'', max_length=100)),
                ('desc', models.CharField(default=b'', max_length=100)),
                ('pub_date', models.DateTimeField(verbose_name=b'date made')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PossTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startTime', models.DateTimeField(verbose_name=b'start time')),
                ('endTime', models.DateTimeField(verbose_name=b'end time')),
                ('nFree', models.IntegerField(default=0)),
                ('peopleList', models.CharField(default=b'', max_length=100)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('refToken', models.CharField(default=b'', max_length=100)),
                ('picture', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('activation_key', models.CharField(max_length=40, blank=True)),
                ('user', models.OneToOneField(related_name='UserProfile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VetoTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startTime', models.DateTimeField(verbose_name=b'start time')),
                ('endTime', models.DateTimeField(verbose_name=b'end time')),
                ('event', models.ForeignKey(to='events.Instance')),
                ('invitee', models.ForeignKey(to='events.Invitee')),
            ],
        ),
    ]

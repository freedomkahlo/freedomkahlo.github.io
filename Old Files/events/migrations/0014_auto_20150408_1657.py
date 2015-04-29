# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_invitee_userid'),
    ]

    operations = [
        migrations.CreateModel(
            name='RsvpInvitee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('userID', models.IntegerField(default='0')),
                ('name', models.CharField(max_length=100)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
        migrations.RemoveField(
            model_name='rsvplist',
            name='event',
        ),
        migrations.DeleteModel(
            name='RsvpList',
        ),
    ]

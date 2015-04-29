# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_instance_creator'),
    ]

    operations = [
        migrations.CreateModel(
            name='RsvpList',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
    ]

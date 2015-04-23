# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Desc',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=20)),
                ('desc', models.CharField(default='description', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Invitee',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(default='John Smith', max_length=100)),
                ('event', models.ForeignKey(to='events.Desc')),
            ],
        ),
    ]

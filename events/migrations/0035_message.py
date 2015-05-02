# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_instance_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=100)),
                ('pub_date', models.DateTimeField(verbose_name=b'date made')),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
    ]

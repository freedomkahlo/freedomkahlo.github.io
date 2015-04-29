# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20150408_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='PossTime',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='poss time')),
                ('votes', models.IntegerField(default=0)),
                ('event', models.ForeignKey(to='events.Instance')),
            ],
        ),
        migrations.AddField(
            model_name='invitee',
            name='hasVoted',
            field=models.BooleanField(default=False),
        ),
    ]

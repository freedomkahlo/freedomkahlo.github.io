# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0007_auto_20150405_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('gcalEmail', models.EmailField(max_length=254)),
                ('picture', models.ImageField(upload_to='profile_images', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='instance',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date made'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='title',
            field=models.CharField(max_length=20, default=''),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]

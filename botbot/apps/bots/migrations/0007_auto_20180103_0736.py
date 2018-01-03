# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0006_auto_20151030_1406'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PersonalChannels',
        ),
        migrations.AlterField(
            model_name='channel',
            name='status',
            field=models.CharField(default=b'PENDING', max_length=20, choices=[(b'PENDING', b'Pending'), (b'ACTIVE', b'Active'), (b'ARCHIVED', b'Archived'), (b'BANNED', b'Banned')]),
        ),
        migrations.AlterField(
            model_name='usercount',
            name='counts',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.IntegerField(), blank=True),
        ),
    ]

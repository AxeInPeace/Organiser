# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-14 21:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_auto_20160514_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distance',
            name='time',
            field=models.TimeField(),
        ),
    ]
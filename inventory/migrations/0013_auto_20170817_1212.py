# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-17 16:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20170817_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costs',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='stock',
            name='date',
            field=models.DateField(default=datetime.datetime(1900, 1, 1, 0, 0)),
        ),
    ]

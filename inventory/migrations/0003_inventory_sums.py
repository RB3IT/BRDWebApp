# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-03 11:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_notesupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='sums',
            field=models.TextField(blank=True, null=True),
        ),
    ]

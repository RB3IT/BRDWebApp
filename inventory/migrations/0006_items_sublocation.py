# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-31 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20170731_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='sublocation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
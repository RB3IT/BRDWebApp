# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-16 15:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_auto_20170816_1027'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('include', models.NullBooleanField()),
                ('itemid', models.ForeignKey(db_column='itemid', on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Items')),
            ],
            options={
                'db_table': 'stock',
            },
        ),
        migrations.AlterField(
            model_name='costs',
            name='cost',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='costs',
            name='price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='quantity',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]

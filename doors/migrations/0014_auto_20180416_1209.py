# Generated by Django 2.0.3 on 2018-04-16 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0013_auto_20180416_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipe',
            name='door',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='doors.Door'),
        ),
    ]

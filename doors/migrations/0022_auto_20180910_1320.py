# Generated by Django 2.0.3 on 2018-09-10 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0021_auto_20180619_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spring',
            name='stretch',
        ),
        migrations.AddField(
            model_name='spring',
            name='casting',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
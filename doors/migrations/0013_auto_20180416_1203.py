# Generated by Django 2.0.3 on 2018-04-16 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0012_accessorybrackets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipe',
            name='pipediameter',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='pipe',
            name='pipelength',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='pipe',
            name='shaftdiameter',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='pipe',
            name='shaftlength',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
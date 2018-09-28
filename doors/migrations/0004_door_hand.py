# Generated by Django 2.0.3 on 2018-04-10 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0003_door_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='door',
            name='hand',
            field=models.CharField(choices=[('R', 'Right'), ('L', 'Left')], default='R', max_length=40),
            preserve_default=False,
        ),
    ]

# Generated by Django 2.0.3 on 2018-04-10 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0002_order_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='door',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]

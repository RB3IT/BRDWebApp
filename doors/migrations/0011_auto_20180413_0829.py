# Generated by Django 2.0.3 on 2018-04-13 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0010_tracks_weatherstripping'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brackets',
            fields=[
                ('bracketid', models.AutoField(primary_key=True, serialize=False)),
                ('bracket_size', models.CharField(max_length=50)),
                ('hand', models.CharField(choices=[('R', 'Right'), ('L', 'Left')], max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='tracks',
            name='bracket_size',
        ),
        migrations.AddField(
            model_name='tracks',
            name='brackets',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='doors.Brackets'),
            preserve_default=False,
        ),
    ]
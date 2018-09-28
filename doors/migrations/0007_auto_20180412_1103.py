# Generated by Django 2.0.3 on 2018-04-12 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doors', '0006_auto_20180412_0953'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('accessory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='doors.Accessory')),
                ('name', models.CharField(choices=[('endlocks', 'Endlocks'), ('rivets', 'Rivets'), ('washers', 'Washers')], max_length=50)),
                ('quantity', models.PositiveIntegerField()),
            ],
            bases=('doors.accessory',),
        ),
        migrations.AlterField(
            model_name='accessory',
            name='kind',
            field=models.CharField(choices=[('motorcover', 'Motor Cover'), ('gearcover', 'Gear Cover'), ('facia', 'Facia'), ('foc', 'FrontofMotorClip'), ('chainplate', 'Chain Plate'), ('slidelocks', 'Slide Locks'), ('pinlocks', 'Pin Locks'), ('feederslat', 'Feeder Slat'), ('hardware', 'Hardware'), ('', 'Other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='slats',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='HardwareEndlocks',
            fields=[
                ('hardware_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='doors.Hardware')),
                ('type', models.CharField(choices=[('FLSTP', 'Flat Stamped'), ('FLCST', 'Flat Cast'), ('FLCWD', 'Flat Cast Windlock'), ('CRCST', 'Curved Cast'), ('CRCWD', 'Curved Cast Windlock'), ('MNCST', 'Mini Cast')], max_length=50)),
                ('continuous', models.BooleanField(default=False)),
            ],
            bases=('doors.hardware',),
        ),
    ]
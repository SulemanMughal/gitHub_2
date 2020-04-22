# Generated by Django 2.2.12 on 2020-04-22 17:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0015_auto_20200414_1826'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consulatation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, error_messages={'blank': 'Consultation Name is Required'}, max_length=100, verbose_name='Consultation Name')),
                ('status', models.CharField(choices=[('None', 'None'), ('New', 'New'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Rejected', 'Rejected')], default='None', max_length=15)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webaccount.Client_Personal_Info')),
            ],
        ),
    ]

# Generated by Django 2.2.12 on 2020-04-22 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0016_consulatation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consulatation',
            options={'verbose_name': 'Consultation', 'verbose_name_plural': 'consultations'},
        ),
        migrations.AlterField(
            model_name='consulatation',
            name='status',
            field=models.CharField(choices=[('None', 'None'), ('New', 'New'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Rejected', 'Rejected')], default='None', error_messages={'blank': 'Consultation Status is Required'}, max_length=15, verbose_name='Consultation Status'),
        ),
    ]
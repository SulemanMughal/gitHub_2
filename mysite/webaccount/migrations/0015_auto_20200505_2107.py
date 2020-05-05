# Generated by Django 2.2.12 on 2020-05-05 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0014_remove_consulatationrequest_clientpaid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consulatationrequest',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Confirmed', 'Confirmed'), ('Pending', 'Pending'), ('Completed', 'Completed'), ('Close', 'Close'), ('Rejected', 'Rejected'), ('Declined', 'Declined')], default='New', max_length=100, verbose_name='Status'),
        ),
    ]
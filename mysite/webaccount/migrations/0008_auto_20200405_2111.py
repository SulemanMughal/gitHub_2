# Generated by Django 2.2 on 2020-04-05 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0007_auto_20200405_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_personal_info',
            name='last_update',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Last Update'),
        ),
    ]
# Generated by Django 2.2 on 2020-04-12 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0006_auto_20200413_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_personal_info',
            name='Name',
            field=models.CharField(error_messages={'blank': 'Name field is empty.', 'unique': 'This name already exists. Try another one.'}, max_length=300, unique=True, verbose_name='Name'),
        ),
    ]

# Generated by Django 2.2.12 on 2020-04-22 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0020_auto_20200422_2334'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consulatationrequest',
            options={'ordering': ['-id'], 'verbose_name': 'Consultation Request', 'verbose_name_plural': 'Consultation Requests'},
        ),
    ]

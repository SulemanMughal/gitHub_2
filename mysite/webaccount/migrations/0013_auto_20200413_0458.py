# Generated by Django 2.2 on 2020-04-12 23:58

from django.db import migrations, models
import webaccount.models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0012_auto_20200413_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_personal_info',
            name='Number_of_branches',
            field=models.IntegerField(default=1, error_messages={'blank': 'Sector can not be left as blank.', 'null': 'Sector Field is not selected'}, validators=[webaccount.models.integerValidator], verbose_name='Number of Branches'),
        ),
        migrations.AlterField(
            model_name='client_personal_info',
            name='Number_of_employees',
            field=models.IntegerField(default=1, error_messages={'blank': 'Sector can not be left as blank.', 'null': 'Sector Field is not selected'}, validators=[webaccount.models.integerValidator], verbose_name='Number of Employees'),
        ),
        migrations.AlterField(
            model_name='client_personal_info',
            name='company_name',
            field=models.CharField(error_messages={'blank': 'Company name is required.', 'null': 'Company name is required.'}, max_length=300, verbose_name='Company Name'),
        ),
        migrations.AlterField(
            model_name='client_personal_info',
            name='contact_number',
            field=models.CharField(error_messages={'blank': 'locationlocation is required.', 'null': 'location is required.'}, max_length=10, validators=[webaccount.models.phoneNumberValidator], verbose_name='Contact Number'),
        ),
        migrations.AlterField(
            model_name='client_personal_info',
            name='location',
            field=models.CharField(error_messages={'blank': 'locationlocation is required.', 'null': 'location is required.'}, max_length=300, verbose_name='Location'),
        ),
    ]
# Generated by Django 2.2.12 on 2020-05-11 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0032_auto_20200511_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultantmodel',
            name='parent',
            field=models.ForeignKey(blank=True, default=28, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='webaccount.ParentModel'),
        ),
    ]
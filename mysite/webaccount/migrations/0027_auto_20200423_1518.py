# Generated by Django 2.2.12 on 2020-04-23 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webaccount', '0026_auto_20200423_1508'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consulatationrequest',
            old_name='client_paid_all_amound',
            new_name='client_paid_all_amount',
        ),
        migrations.AlterField(
            model_name='consulatationrequest',
            name='client_paid',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, max_length=100, null=True, verbose_name='Client Paid Amound'),
        ),
    ]
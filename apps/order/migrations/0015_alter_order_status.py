# Generated by Django 4.2.14 on 2024-12-12 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('canceled', 'Canceled'), ('delivered', 'Delivered'), ('completed', 'Completed')], default='paid', max_length=20),
        ),
    ]
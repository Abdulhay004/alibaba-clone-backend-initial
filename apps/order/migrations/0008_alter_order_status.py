# Generated by Django 4.2.14 on 2024-12-10 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_alter_order_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('canceled', 'Canceled'), ('delivered', 'Delivered'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
    ]

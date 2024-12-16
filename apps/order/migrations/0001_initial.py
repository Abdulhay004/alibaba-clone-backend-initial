# Generated by Django 4.2.14 on 2024-12-16 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0004_alter_product_stock'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_method', models.CharField(choices=[('click', 'Click'), ('payme', 'Payme'), ('card', 'Card'), ('paypal', 'Paypal')], max_length=20)),
                ('country_region', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state_province_region', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_zip_code', models.CharField(max_length=20)),
                ('telephone_number', models.CharField(max_length=50, null=True)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('canceled', 'Canceled'), ('delivered', 'Delivered'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('transaction_id', models.CharField(max_length=100, null=True, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.product')),
            ],
        ),
    ]

# Generated by Django 4.2.14 on 2024-11-07 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('user', '0006_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='permissions',
            field=models.ManyToManyField(blank=True, null=True, related_name='policy_permissions', to='auth.permission'),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='user.group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='policies',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='user.policy'),
        ),
    ]

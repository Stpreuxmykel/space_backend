# Generated by Django 5.1 on 2024-11-13 20:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkapp', '0014_googleuser_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interestgoogle',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='linkapp.googleuser'),
        ),
    ]

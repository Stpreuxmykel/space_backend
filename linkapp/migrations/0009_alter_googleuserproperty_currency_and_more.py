# Generated by Django 5.1.1 on 2024-09-25 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkapp', '0008_alter_googleuserproperty_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='googleuserproperty',
            name='currency',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='googleuserproperty',
            name='decision',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='googleuserproperty',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='userproperty',
            name='currency',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='userproperty',
            name='decision',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userproperty',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
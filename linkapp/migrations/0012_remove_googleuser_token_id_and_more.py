# Generated by Django 5.1 on 2024-11-13 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linkapp', '0011_alter_googleuser_token_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googleuser',
            name='token_id',
        ),
        migrations.RemoveField(
            model_name='googleuserprofile',
            name='token_id',
        ),
        migrations.RemoveField(
            model_name='interestgoogle',
            name='token_id',
        ),
    ]
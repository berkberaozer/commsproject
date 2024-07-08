# Generated by Django 5.0.6 on 2024-07-05 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_rename_isonline_user_online'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='chat',
            constraint=models.UniqueConstraint(fields=('belong', 'target'), name='unique_chat'),
        ),
    ]

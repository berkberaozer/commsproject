# Generated by Django 5.0.6 on 2024-07-16 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_user_pass_phrase_alter_status_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pass_phrase',
            field=models.CharField(default=123, max_length=255),
            preserve_default=False,
        ),
    ]

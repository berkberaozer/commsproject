# Generated by Django 5.0.6 on 2024-07-16 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_user_public_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pass_phrase',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='public_key',
            field=models.TextField(blank=True, null=True),
        ),
    ]

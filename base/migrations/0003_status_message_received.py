# Generated by Django 5.0.6 on 2024-07-12 11:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_chat_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_reached', models.BooleanField(default=False)),
                ('has_read', models.BooleanField(default=False)),
                ('has_sent', models.BooleanField(default=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='base.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='received',
            field=models.ManyToManyField(related_name='received_messages', through='base.Status', to=settings.AUTH_USER_MODEL),
        ),
    ]
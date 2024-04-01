# Generated by Django 5.0.3 on 2024-03-30 07:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_message_id_alter_mgroup_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='mgroup',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='created_mgroups', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

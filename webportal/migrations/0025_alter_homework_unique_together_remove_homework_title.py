# Generated by Django 5.1.7 on 2025-06-03 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webportal', '0024_attendance'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='homework',
            unique_together={('subject', 'assigned_date')},
        ),
        migrations.RemoveField(
            model_name='homework',
            name='title',
        ),
    ]

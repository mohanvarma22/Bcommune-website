# Generated by Django 5.1.4 on 2025-02-01 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_internshipapplication_match_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internshipapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected'), ('accepted', 'Accepted')], default='pending', max_length=20),
        ),
    ]

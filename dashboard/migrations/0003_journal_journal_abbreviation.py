# Generated by Django 5.1.6 on 2025-03-17 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_volume_article_article_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='journal_abbreviation',
            field=models.CharField(default='j', help_text='e.g: IJPRSS', max_length=1000),
        ),
    ]

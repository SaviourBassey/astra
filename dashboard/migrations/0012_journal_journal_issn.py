# Generated by Django 5.1.6 on 2025-05-01 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_alter_article_article_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='journal_ISSN',
            field=models.CharField(default='0', max_length=1000),
        ),
    ]

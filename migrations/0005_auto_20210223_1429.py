# Generated by Django 3.1.2 on 2021-02-23 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210222_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='parent',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
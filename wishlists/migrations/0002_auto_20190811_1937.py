# Generated by Django 2.2.4 on 2019-08-11 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlists', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='key_text',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]

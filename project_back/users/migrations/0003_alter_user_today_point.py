# Generated by Django 4.1.3 on 2022-11-22 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_retention_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='today_point',
            field=models.BooleanField(default=False, verbose_name='오늘 포인트받은 여부'),
        ),
    ]

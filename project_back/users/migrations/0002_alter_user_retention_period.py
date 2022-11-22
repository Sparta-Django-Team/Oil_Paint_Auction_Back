from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='retention_period',
            field=models.TextField(choices=[('2023-11-22', '1year')], default='2023-11-22', verbose_name='회원정보 보유기간'),
        ),
    ]

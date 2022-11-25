from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_term_check'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='retention_period',

            field=models.TextField(choices=[('2023-11-25', '1year')], default='2023-11-25', verbose_name='회원정보 보유기간'),

        ),
        migrations.AlterField(
            model_name='user',
            name='term_check',
            field=models.BooleanField(default=False, null=True, verbose_name='약관 동의 여부'),
        ),
    ]
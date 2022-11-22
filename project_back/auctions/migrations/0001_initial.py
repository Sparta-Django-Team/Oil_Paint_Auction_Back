# Generated by Django 4.1.3 on 2022-11-22 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_bid', models.PositiveIntegerField(default=10000, verbose_name='시작 입찰가')),
                ('now_bid', models.PositiveIntegerField(null=True, verbose_name='현재 입찰가')),
                ('last_bid', models.PositiveIntegerField(null=True, verbose_name='최종 입찰가')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='경매 시작')),
                ('end_date', models.DateTimeField(null=True, verbose_name='경매 마감')),
                ('auction_like', models.ManyToManyField(blank=True, related_name='like_auction', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auction',
                'ordering': ['id'],
            },
        ),
    ]

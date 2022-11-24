from django.db import models

from users.models import User
from paintings.models import Painting

class Auction(models.Model):
    start_bid = models.PositiveIntegerField('시작 입찰가', default=10000)
    now_bid = models.PositiveIntegerField('현재 입찰가', null=True, blank=True)
    last_bid = models.PositiveIntegerField('최종 입찰가', null=True, blank=True)
    start_date = models.DateTimeField('경매 시작', auto_now_add=True)
    end_date = models.DateTimeField('경매 마감', null=True)
    
    painting = models.OneToOneField(Painting, verbose_name='유화', on_delete=models.CASCADE)
    auction_like = models.ManyToManyField(User, verbose_name='경매 좋아요', related_name='like_auction', blank=True)

    class Meta:
        db_table = 'auction'
        ordering = ['id']

    def __str__(self):
        return f'[제목]{self.painting.title}'

class Comment(models.Model):
    comment = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'db_comment'
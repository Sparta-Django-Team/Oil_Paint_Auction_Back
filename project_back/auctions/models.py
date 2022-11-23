from django.db import models

from users.models import User
from paintings.models import Painting

class Auction(models.Model):
    author = models.ForeignKey('작성자', User, on_delete=models.CASCADE)
    painting = models.ForeignKey('유화', Painting, on_delete=models.CASCADE)

    start_bid = models.PositiveIntegerField('시작 입찰가', default=10000)
    now_bid = models.PositiveIntegerField('현재 입찰가', null=True,blank=True)
    last_bid = models.PositiveIntegerField('최종 입찰가', null=True, blank=True)

    start_date = models.DateTimeField('경매 시작', auto_now_add=True)
    end_date = models.DateTimeField('경매 마감', null=True)

    auction_like = models.ManyToManyField('경매 좋아요', User, related_name="like_auction",blank=True)

    class Meta: 
        db_table = 'auction'
        ordering = ['id']

    def __str__(self):
        return str(self.painting.title)
from django.db import models

from users.models import User
from paintings.models import Painting

class Auction(models.Model):
    start_bid = models.PositiveIntegerField('시작 입찰가', default=10000)
    now_bid = models.PositiveIntegerField('현재 입찰가', null=True, blank=True)
    last_bid = models.PositiveIntegerField('최종 입찰가', null=True, blank=True)
    start_date = models.DateTimeField('경매 시작', auto_now_add=True)
    end_date = models.DateTimeField('경매 마감', null=True)
    

    painting = models.OneToOneField(Painting, verbose_name="유화",on_delete=models.CASCADE)
    auction_like = models.ManyToManyField(User, verbose_name='경매 좋아요', related_name="like_auction",blank=True)
    bidder = models.ForeignKey(User,  verbose_name='입찰자', on_delete=models.SET_NULL, null=True, blank=True, related_name='auction_bidder')
    


    class Meta:
        db_table = 'auction'
        ordering = ['id']

    def __str__(self):
        return f'[제목]{self.painting.title}, [원작자]{self.painting.author}, [소유자]{self.painting.owner}'

class Comment(models.Model):
    content = models.TextField('내용', max_length=100)
    created_at = models.DateTimeField('생성 시간', auto_now_add=True)
    updated_at = models.DateTimeField('수정 시간', auto_now = True)

    user = models.ForeignKey(User, verbose_name='작성자', on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, verbose_name='경매 작품', on_delete=models.CASCADE, related_name="comment")

    class Meta:
        db_table = 'db_comment'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'[작성자]{self.user}, [내용]{self.content}'
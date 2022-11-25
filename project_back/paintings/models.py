from django.db import models

from users.models import User

STYLE_CHOICES = (
        ('1','composition'),
        ('2','la_muse'),
        ('3','starry_night'),
        ('4','the_wave'),
        ('5','candy'),
        ('6','feathers'),
        ('7','mosaic'),
        ('8','the_scream'),
        ('9','udnie'),
    )

class Painting(models.Model):
    
    title = models.CharField('제목', null=True, blank=True, max_length=20)
    content = models.TextField('내용', null=True, blank=True, max_length=200)
    before_image = models.ImageField('변환 전 사진', blank=True, upload_to='before_img')
    after_image = models.ImageField('변환 후 사진', blank=True, upload_to='after_img')
    created_at = models.DateTimeField('생성 시간', auto_now_add=True)
    updated_at = models.DateTimeField('수정 시간', auto_now=True)
    style = models.CharField('스타일', max_length=20, choices=STYLE_CHOICES)
    is_auction = models.BooleanField('경매상태', default=False)
    
    author = models.ForeignKey(User, verbose_name='원작자',on_delete=models.PROTECT, null=True, related_name='author_painting' )
    owner = models.ForeignKey(User,  verbose_name='소유자',on_delete=models.PROTECT, null=True, related_name='owner_painting')
    class Meta:
        db_table = 'db_painting'

    def __str__(self):
        return f'[제목]{self.title}'


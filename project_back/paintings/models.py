from django.db import models

from users.models import User

class Painting(models.Model):
    STYLE_CHOICES = (
        ('Composition_vii','01_eccv16_composition_vii.t7'),
        ('La_muse(1)','02_eccv16_la_muse.t7'),
        ('Starry_night(1)','03_eccv16_starry_night.t7'),
        ('The_wave','04_eccv16_the_wave.t7'),
        ('Candy','05_instance_norm_candy.t7'),
        ('Feathers','06_instance_norm_feathers.t7'),
        ('La_muse(2)','07_instance_norm_la_muse.t7'),
        ('Mosaic','08_instance_norm_mosaic.t7'),
        ('Starry_night(2)','09_instance_norm_starry_night.t7'),
        ('The_scream','10_instance_norm_the_scream.t7'),
        ('Udnie','11_instance_norm_udnie.t7'),
    )
    
    title = models.CharField('제목', max_length=20, blank=True)
    content = models.TextField('내용', max_length=200, blank=True)
    before_image = models.ImageField('변환 전 사진', blank=True, upload_to='before_img')
    after_image = models.ImageField('변환 후 사진',blank=True, upload_to='after_img')
    created_at = models.DateTimeField('생성 시간',auto_now_add=True)
    updated_at = models.DateTimeField('수정 시간',auto_now=True)
    style = models.CharField('스타일', max_length=20, choices=STYLE_CHOICES)
    is_auction = models.BooleanField('경매상태', default=False)

    author = models.ForeignKey(User, verbose_name='원작자',on_delete=models.PROTECT, related_name='author_painting' )
    owner = models.ForeignKey(User,  verbose_name='소유자',on_delete=models.PROTECT, null=True, related_name='owner_painting')
    
    class Meta: 
        db_table = 'db_painting'

    def __str__(self):
        return f'[제목]{self.title}'
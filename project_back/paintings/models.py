from django.db import models

from users.models import User
class PaintStyle(models.Model):
    model_name = models.CharField(max_length=70, blank=True)
    model_urls = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return str(self.model_name)

class Painting(models.Model):
    title = models.CharField('제목', max_length=20, blank=True)
    content = models.TextField('내용', max_length=200, blank=True)
    before_image = models.ImageField('변환 전 사진', blank=True, upload_to='before_img')
    after_image = models.ImageField('변환 후 사진',blank=True, upload_to='after_img')
    paint_style = models.ForeignKey(PaintStyle, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField('생성 시간',auto_now_add=True)
    updated_at = models.DateTimeField('수정 시간',auto_now=True)
    
    author = models.ForeignKey('작성자', User, on_delete=models.CASCADE)
    
    class Meta: 
        db_table = 'db_painting'

    def __str__(self):
        return str(self.title)
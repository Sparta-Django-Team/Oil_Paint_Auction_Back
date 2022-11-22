from users.models import User
from django.db import models

class PaintStyle(models.Model):
    model_name = models.CharField(max_length=70, blank=True)
    model_urls = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return str(self.model_name)

class Painting(models.Model):
    title = models.CharField(max_length=20, blank=True)
    content = models.TextField(max_length=200, blank=True)
    before_image = models.ImageField(blank=True, upload_to='before_img')
    after_image = models.ImageField(blank=True, upload_to='after_img')
    paint_style = models.ForeignKey(PaintStyle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta: 
        db_table = 'db_painting'

    def __str__(self):
        return str(self.title)
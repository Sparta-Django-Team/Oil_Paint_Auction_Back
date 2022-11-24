from django.contrib import admin

from .models import Auction, Comment

admin.site.register(Auction)
admin.site.register(Comment)

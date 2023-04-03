# django
from django.contrib import admin

# auctions
from auctions.models import Auction, Comment, AuctionHistory


class AuctionHistoryInline(admin.StackedInline):
    model = AuctionHistory


class CommentInline(admin.StackedInline):
    model = Comment


class AuctionAdmin(admin.ModelAdmin):
    inlines = (
        AuctionHistoryInline,
        CommentInline,
    )


admin.site.register(Auction, AuctionAdmin)
admin.site.register(Comment)

# django
from django.urls import path

# auctions
from . import views

urlpatterns = [
    # Auction
    path("", views.AuctionListView.as_view(), name="auction_list_view"),
    path("mylist/", views.AuctionMyListView.as_view(), name="auction_mylist_view"),
    path("<int:painting_id>/", views.AuctionCreateView.as_view(), name="auction_create_view"),
    path("detail/<int:auction_id>/", views.AuctionDetailView.as_view(), name="auction_detail_view"),
    path("<int:auction_id>/likes/", views.AuctionLikeView.as_view(), name="auction_like_view"),
    path("<int:auction_id>/history/", views.AuctionHistoryView.as_view(), name="auction_history_view"),
    path("search/", views.AuctionSearchView.as_view(), name="auction_search_view"),
    
    # Auction Comment
    path("<int:auction_id>/comments/", views.CommentView.as_view(), name="comment_view"),
    path("<int:auction_id>/comments/<int:comment_id>/", views.CommentDetailView.as_view(), name="comment_detail_view"),
]

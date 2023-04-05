# django
from django.urls import path

# auctions
from auctions import views

urlpatterns = [
    # Auction
    path("", views.AuctionListView.as_view(), name="auction_list"),
    path("my/", views.AuctionMyListView.as_view(), name="auction_mylist"),
    path("paintings/<int:painting_id>/", views.AuctionCreateView.as_view(), name="auction_create"),
    path("<int:auction_id>/", views.AuctionDetailView.as_view(), name="auction_detail"),
    path("<int:auction_id>/likes/", views.AuctionLikeView.as_view(), name="auction_like"),
    path("<int:auction_id>/history/", views.AuctionHistoryView.as_view(), name="auction_history"),
    path("search/", views.AuctionSearchView.as_view(), name="auction_search"),
    
    # Auction Comment
    path("<int:auction_id>/comments/", views.CommentView.as_view(), name="comment"),
    path("<int:auction_id>/comments/<int:comment_id>/", views.CommentDetailView.as_view(), name="comment_detail"),
]

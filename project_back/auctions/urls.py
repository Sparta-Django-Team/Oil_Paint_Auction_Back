from django.urls import path

from . import views


urlpatterns = [
    path('',views.AuctionListView.as_view(), name='auction_list_view'),
    path('<int:painting_id>/', views.AuctionCreateView.as_view(), name='auction_create_view'),
    path('detail/<int:auction_id>/',views.AuctionDetailView.as_view(), name='auction_detail_view'),    
    path('<int:auction_id>/likes/',views.AuctionLikeView.as_view(), name="auction_like_view"),

    ## Comment
    path('<int:auction_id>/comments/', views.CommentView.as_view(), name="comment_view"),
    path('<int:auction_id>/comments/<int:comment_id>/', views.CommentDetailView.as_view(), name="comment_detail_view"),
]
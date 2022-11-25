from django.urls import path,include
from paintings import views
from auctions import views

urlpatterns = [
    path('', views.PaintingListview.as_view(), name='painting_list_view'),
    path('<int:user_id>/<int:painting_id>/', views.PaintingDetailView.as_view(), name ='painting_detail_view'),
    path('style/', views.PaintingStyleSelectView.as_view(), name='style_select_view'),
    path('img/', views.ImageUploadView.as_view(), name='image_upload_view'),
    path('img/<int:painting_id>/', views.PaintingCreateView.as_view(), name='painting_create_view'),
]

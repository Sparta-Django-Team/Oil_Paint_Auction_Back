from django.urls import path
from paintings import views

urlpatterns = [
    # Image style
    path('styles/', views.PaintingStyleSelectView.as_view(), name='style_select'),
    path('images/', views.ImageUploadView.as_view(), name='image_upload'),
    
    # Painting
    path('', views.PaintingListview.as_view(), name='painting_list'),
    path('<int:painting_id>/', views.PaintingDetailView.as_view(), name='painting_detail'),
]

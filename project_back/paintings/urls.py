from django.urls import path
from paintings import views

urlpatterns = [
    #Image style
    path('style/', views.PaintingStyleSelectView.as_view(), name='style_select_view'),
    path('img/', views.ImageUploadView.as_view(), name='image_upload_view'),
    
    #Painting
    path('', views.PaintingListview.as_view(), name='painting_list_view'),
    path('img/<int:painting_id>/', views.PaintingCreateView.as_view(), name='painting_create_view'),
    path('<int:painting_id>/', views.PaintingDetailView.as_view(), name='painting_detail_view'),
]

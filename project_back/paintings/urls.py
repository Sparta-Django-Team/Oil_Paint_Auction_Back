from django.urls import path

from paintings import views

urlpatterns = [
    path('', views.PaintingListview.as_view(), name='painting_list_view'),
    path('img/<int:painting_id>/', views.PaintingCreateView.as_view(), name='painting_create_view'),
    path('<int:painting_id>/', views.PaintingDetailView.as_view(), name='painting_detail_view'),
    path('style/', views.PaintingStyleSelectView.as_view(), name='style_select_view'),
    path('img/', views.ImageUploadView.as_view(), name='image_upload_view'),
<<<<<<< HEAD
    path('img/<int:painting_id>/', views.PaintingCreateView.as_view(), name='painting_create_view'),
    # path('<int:painting_id>/',)
=======
>>>>>>> 9e9b5613c16b82d4d6a0ca7d66b364d1a740ac82
]

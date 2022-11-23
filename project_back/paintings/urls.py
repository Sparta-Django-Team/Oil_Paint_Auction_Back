from django.urls import path

from paintings import views

urlpatterns = [
    path('style', views.PaintingStyleSelectView.as_view(), name='styleselect_view'),
    path('file', views.ImageUploadView.as_view(), name='imageupload_view'),
    path('new/<int:painting_id>', views.PaintingCreateView.as_view(), name='paintingcreate_view'),
]


from django.urls import path

from paintings import views

urlpatterns = [
    path('styles', views.PaintingStyleSelectView.as_view(), name='styleselect_view'),
    path('imgs/<int:style_num>', views.ImageUploadView.as_view(), name='imageupload_view'),
    # path('imgs', views.PaintingCreateView.as_view(), name='paintingcreate_view'),
]


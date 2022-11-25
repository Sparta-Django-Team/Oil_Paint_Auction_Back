from django.urls import path,include
from paintings import views
from auctions import views

urlpatterns = [
    # path('styles', views.PaintingStyleSelectView.as_view(), name='styleselect_view'),
    path('<int:user_id>/<int:painting_id>/', views.PaintingDetailView.as_view(), name ='painting_detail_view'),
    path('imgs/<int:style_num>', views.ImageUploadView.as_view(), name='imageupload_view'),
    # path('imgs', views.PaintingCreateView.as_view(), name='paintingcreate_view'),
]


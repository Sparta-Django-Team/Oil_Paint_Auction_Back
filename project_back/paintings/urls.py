from django.urls import path

from . import views

urlpatterns = [
    path('styleselect/', views.PaintingStyleSelectView.as_view(), name='styleselect_view'),
    path('<int:style_no>/', views.PaintingCreateView.as_view(), name='paintingcreate_view'),
]
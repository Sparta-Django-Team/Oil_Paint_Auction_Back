from django.urls import path, include
from paintings import views

urlpatterns = [
    path('<int:painting_id>/', views.PaintingDetailView.as_view(), name='painting_view'),
    
]

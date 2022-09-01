from django.urls import path
from . import views


urlpatterns = [
    path('', views.get_PostList),
    path('<int:pk>/', views.get_Post),
]
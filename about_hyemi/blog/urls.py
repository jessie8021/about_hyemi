from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.get_PostList),
    path('<int:pk>/', views.get_Post),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
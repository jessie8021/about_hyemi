from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'
urlpatterns = [
    path('post/', views.PostList.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name='post-detail'),
    path('post/<int:category>/category/', views.get_postsCategory),
    path('category/', views.CategoryList.as_view(), name='category-list'),
    path('category/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

app_name = 'blog'

router = DefaultRouter()
router.register(r'tag', views.TagViewSet)
urlpatterns = [
    path('post/', views.PostList.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name='post-detail'),
    path('post/<int:category>/category/', views.get_postsCategory),
    path('post/<int:tag>/tag/', views.get_postsTag),
    path('category/', views.CategoryList.as_view(), name='category-list'),
    path('category/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
    path('', include(router.urls)),
    path('comment/', views.CommentList.as_view()),
    path('comment/<int:pk>/', views.CommentDetail.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
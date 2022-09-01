
"""
logout
    allauth 에서 로그아웃 구현되어 있음.
    ex) http://localhost:8000/accounts/logout/
    body = {"refresh" : "refresh token"}
    header =  csrftoken : 로그인 시, cookie 에 저장된 값.
"""

from django.urls import path, include

from .views import *
# get refresh token
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    # Google login
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('google/login/finish/', GoogleLogin.as_view(), name='google_login_todjango'),

    # Kakao login
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/callback/', kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),

    # github login
    path('github/login/', github_login, name='github_login'),
    path('github/callback/', github_callback, name='github_callback'),
    path('github/login/finish/', GithubLogin.as_view(), name='github_login_todjango'),

    # naver login
    path('naver/login/', naver_login, name='naver_login'),
    path('naver/callback/', naver_callback, name='naver_callback'),
    path('naver/login/finish/', NaverLogin.as_view(), name='naver_login_todjango'),


    # get refresh token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect

from json.decoder import JSONDecodeError

import requests

from .models import CustomUser

from rest_framework import status

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.github import views as github_view
from allauth.socialaccount.providers.naver import views as naver_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from dj_rest_auth.registration.views import SocialLoginView

state = getattr(settings, 'STATE')

BASE_URL = 'http://127.0.0.1:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'
KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/callback/'
GITHUB_CALLBACK_URI = BASE_URL + 'accounts/github/callback/'
NAVER_CALLBACK_URI = BASE_URL + 'accounts/naver/callback/'


def google_login(request):
    """
    Code Request : 로그인 성공시, Callback 함수로 Code값 전달받음
    매칭된 url로 들어가면, client_id, redirect_uri 등과 같은 정보를
    url parameter로 함께 보내 리다이렉트 한다.
    구글 로그인 창이 뜨고, 알맞는 아이디, 비밀번호로 진행하면 Callback URI로
    Code 값이 들어가게 된다.
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    request = redirect(f"https://accounts.google.com/o/oauth2/v2/auth?"
                       f"client_id={client_id}&"
                       f"response_type=code&"
                       f"redirect_uri={GOOGLE_CALLBACK_URI}&"
                       f"scope={scope}")
    return request


def google_callback(request):
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')

    '''
    Access Token Request : google_login에서 받은 Code로 Google에 AccessToken 요청

    Google API Server에 응답받은 Code, client_secret, state와 같은 url paramter를
    함께 Post요청을 보낸다. 성공하면, access_token 을 가져올 수 있다.
    '''
    token_req = requests.post(f"https://oauth2.googleapis.com/token?"
                              f"client_id={client_id}&"
                              f"client_secret={client_secret}&"
                              f"code={code}&"
                              f"grant_type=authorization_code&"
                              f"redirect_uri={GOOGLE_CALLBACK_URI}&"
                              f"state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')

    '''
    Email Request : AccessToken으로 Email 값을 Google에게 요청

    AccessToken을 로그인된 사용사의 Email을 응답받기 위해 url parameter에 포함하여 요청
    '''
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?"
                             f"access_token={access_token}")
    email_req_staus = email_req.status_code

    if email_req_staus != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)

    email_req_json = email_req.json()
    email = email_req_json.get('email')

    '''
    Signup or Signin Request : Email, AccessToken, Code를 바탕으로 회원가입/로그인 진행

    전달 받은 Email 과 동일한 Email이 있는 지 매칭
    - 있는 경우
        ✔︎ FK 로 연결되어 있는 socialaccount 테이블에서 이메일의 유저가 있는 지 체크
        ✔︎ 없으면 일반계정이므로, 에러 메세지와 함께 400 리턴
        ✔︎ 있지만 다른 Provider로 가입되어 있으면 에러 메세지와 함께 400 리턴
        ✔︎ 위 두개에 걸리지 않으면 로그인 진행, 해당 유저의 JWT발급, 
        ✔︎ 예기치 못한 오류가 발생하면 에러 메세지와 함께 오류 Status 응답
    - 없는 경우(신규 유저) 
        ✔︎  회원가입 진행 및 해당 유저의 JWT발급
        ✔︎ 예기치 못한 오류가 발생하면 에러 메세지와 함께 오류 Status 응답
    '''
    try:
        user = CustomUser.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        # 기가입 유저의 Provider가 Google인 아닌 경우
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        # Google로 가입된 유저
        data = {'access_token': access_token}
        # data = {'access_token': access_token, 'code': code}

        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


    # 기존 가입된 유저가 아닌경우, 새로 가입
    except CustomUser.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    return redirect(f"https://kauth.kakao.com/oauth/authorize?"
                    f"client_id={rest_api_key}&"
                    f"redirect_uri={KAKAO_CALLBACK_URI}&"
                    f"response_type=code")


def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get('code')
    redirect_uri = KAKAO_CALLBACK_URI

    '''
    Access Token Request
    '''
    token_req = requests.get(f"https://kauth.kakao.com/oauth/token?"
                             f"grant_type=authorization_code&"
                             f"client_id={rest_api_key}&"
                             f"redirect_uri={redirect_uri}&"
                             f"code={code}")
    token_req_json = token_req.json()
    error = token_req_json.get('error')
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")

    '''
    Email Request
    '''
    profile_request = requests.get("https://kapi.kakao.com/v2/user/me",
                                   headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    error = profile_json.get('error')
    if error is not None:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get('kakao_account')
    email = kakao_account.get('email')

    '''
    Signup or Signin Request
    '''
    try:
        user = CustomUser.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except CustomUser.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


def github_login(request):
    client_id = getattr(settings, 'SOCIAL_AUTH_GITHUB_CLIENT_ID')
    return redirect(f"https://github.com/login/oauth/authorize?"
                    f"client_id={client_id}&"
                    f"redirect_uri={GITHUB_CALLBACK_URI}")


def github_callback(request):
    client_id = getattr(settings, 'SOCIAL_AUTH_GITHUB_CLIENT_ID')
    client_secret = getattr(settings, 'SOCIAL_AUTH_GITHUB_SECRET')
    code = request.GET.get('code')

    '''
    Access Token Request
    '''
    token_req = requests.post(f"https://github.com/login/oauth/access_token?"
                              f"client_id={client_id}&"
                              f"client_secret={client_secret}&"
                              f"code={code}&"
                              f"accept=&json&"
                              f"redirect_uri={GITHUB_CALLBACK_URI}&"
                              f"response_type=code", headers={'Accept': 'application/json'})
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get('access_token')

    '''
    Email Request
    '''
    user_req = requests.get(f"https://api.github.com/user",
                            headers={"Authorization": f"Bearer {access_token}"})

    user_json = user_req.json()
    error = user_json.get('error')

    if error is not None:
        raise JSONDecodeError(error)
    email = user_json.get('email')

    '''
    Signup or Signin Request
    '''
    try:
        user = CustomUser.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'github':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/github/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except CustomUser.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/github/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class GithubLogin(SocialLoginView):
    adapter_class = github_view.GitHubOAuth2Adapter
    callback_url = GITHUB_CALLBACK_URI
    client_class = OAuth2Client


def naver_login(request):
    client_id = getattr(settings, 'SOCIAL_AUTH_NAVER_CLIENT_ID')
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?"
                    f"response_type=code&"
                    f"client_id={client_id}&"
                    f"redirect_uri={NAVER_CALLBACK_URI}&"
                    f"state={state}")


def naver_callback(request):
    client_id = getattr(settings, 'SOCIAL_AUTH_NAVER_CLIENT_ID')
    client_secret = getattr(settings, 'SOCIAL_AUTH_NAVER_SECRET')
    code = request.GET.get('code')

    '''
    Access Token Request
    '''
    token_req = requests.post(f"https://nid.naver.com/oauth2.0/token?"
                              f"grant_type=authorization_code&"
                              f"client_id={client_id}&"
                              f"client_secret={client_secret}&"
                              f"code={code}&"
                              f"state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get('error')
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")

    '''
    Email Request
    '''
    user_req = requests.get(f"https://openapi.naver.com/v1/nid/me",
                            headers={"Authorization": f"Bearer {access_token}"})

    user_json = user_req.json()
    error = user_json.get('error')

    if error is not None:
        raise JSONDecodeError(error)
    email = user_json.get('email')

    '''
    Signup or Signin Request
    '''
    try:
        user = CustomUser.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'naver':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except CustomUser.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client


from rest_framework import viewsets
from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
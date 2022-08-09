
"""opensocialmediaapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import random
import string
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
import smtplib
import os
import tweepy
import email
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from opensocialmediaapp.api import views
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .api.models import User, UserLoginTokens
from django.contrib.auth.hashers import make_password, check_password
import environ
from django.core.exceptions import ImproperlyConfigured
import jwt
import time
from mailer import Mailer
env = environ.Env()
environ.Env.read_env()


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'instagram', views.InstagramViewSet)


def token_response(access_token: str, refresh_token: str):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def signJWT(user_id: str):
    jwt_algorithm = env('algorithm')
    jwt_secret = env('secret')
    access_payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    refresh_payload = {
        "user_id": user_id,
        "expires": time.time() + 30000000
    }
    access_token = jwt.encode(
        access_payload, jwt_secret, algorithm=jwt_algorithm)
    refresh_token = jwt.encode(
        refresh_payload, jwt_secret, algorithm=jwt_algorithm)
    return token_response(access_token, refresh_token)


def new_token_response(access_token: str):
    return {
        "access_token": access_token
    }


def sign_new_jwt(user_id: str):
    jwt_algorithm = env('algorithm')
    jwt_secret = env('secret')
    access_payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    access_token = jwt.encode(
        access_payload, jwt_secret, algorithm=jwt_algorithm)
    return new_token_response(access_token)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):

    # find the user base in params
    user = User.objects.filter(email=request.data['username'])

    if not user:
        return Response({'Error': 'No user found with those details'})

    hashed_password = user[0].password
    user_id = user[0].id

    check = check_password(request.data['password'], hashed_password)

    if check == False:
        return Response({'Error': 'No user found with those details'})

    token = signJWT(user_id)

    access_token = token['access_token']
    refresh_token = token['refresh_token']

    saved_token = UserLoginTokens.objects.create(
        access_token=access_token, refresh_token=refresh_token, user_id=user_id
    )
    saved_token.save()
    return Response({
        'access': access_token,
        'refresh': refresh_token,
        'id': user_id
    })


def decodeJWT(token: str) -> dict:
    print(token, 'token1234')
    try:
        jwt_algorithm = env('algorithm')
        jwt_secret = env('secret')
        decoded_token = jwt.decode(
            token, jwt_secret, algorithms=[jwt_algorithm])
        return decoded_token if decoded_token['expires'] <= time.time() else None
    except Exception as e:
        print(e, 'eeee')
        return {}


def reIssueAccessToken(token):

    def decodeJWT(token: str) -> dict:
        jwt_algorithm = env('algorithm')
        jwt_secret = env('secret')
        decoded_token = jwt.decode(
            token, jwt_secret, algorithms=[jwt_algorithm])
        print(decoded_token, 'daniel123')
        return decoded_token if decoded_token['expires'] <= time.time() else None

    print(token, 'token321')
    new_decoded = decodeJWT(token)
    print(new_decoded, 'new_decoded')

    new_token = sign_new_jwt(new_decoded['user_id'])

    # await save_token_in_db(new_token, str(new_decoded['user_id']))
    UserLoginTokens.objects.filter(
        user_id=new_decoded['user_id']).update(access_token=new_token)
    return new_token


@api_view(['GET'])
@permission_classes([AllowAny])
def refresh_token(request):

    refresh_token = request.headers.get('x-refresh')

    bearer_token = request.headers.get('authorization')

    if refresh_token is None or bearer_token is None:
        return {"error": "Missing token"}

    access_token = bearer_token[7:]

    isAllowed = decodeJWT(access_token)

    if isAllowed is None and refresh_token:
        new_access_token = reIssueAccessToken(access_token)
        return Response({'Success': str(new_access_token)})
    return Response({})


@api_view(['GET'])
def twitter(request):
    # SECRET_KEY = env('SECRET_KEY')
    auth = tweepy.OAuthHandler(env('API_KEY'), env('API_SECRET_KEY'))
    auth.set_access_token(env('ACCESS_TOKEN'), env('ACCESS_SECRET_TOKEN'))
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        print('Successful Authentication')
    except:
        print('Failed authentication')
    # Store user as a variable
    user = api.get_user(screen_name='entertainingdan')
    print(user, 'user123')
    # Get user Twitter statistics
    print(f"user.followers_count: {user.followers_count}")
    print(f"user.listed_count: {user.listed_count}")
    print(f"user.statuses_count: {user.statuses_count}")

    # Show followers
    for follower in user.followers():
        print('Name: ' + str(follower.name))
        print('Username: ' + str(follower.screen_name))
    tweets = []
    for i in tweepy.Cursor(api.search_tweets,
                           q='from:user -filter:retweets',
                           tweet_mode='extended').items():
        tweets.append(i.full_text)
    print(len(tweets), 'tweets')


def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


@api_view(['POST'])
def reset_password(request):
    size = 12

    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_password = random_string_generator(size, letters)
    email = request.data['email']
    user = User.objects.filter(email=email)
    if not user:
        return Response({'Error': 'No user found with those details'})

    message = {
        'personalizations': [
            {
                'to': [
                    {
                        'email': email
                    }
                ],
                'subject': 'Password reset request'
            }
        ],
        'from': {
            'email': 'danibeamo@hotmail.com'
        },
        'content': [
            {
                'type': 'text/plain',
                'value': f'Your new temporary password for Dans App is: {random_password}'
            }
        ]
    }
    hashed_password = make_password(random_password)

    try:
        sg = SendGridAPIClient(os.environ.get(
            env('SENDGRID_API_KEY')))
        response = sg.send(message)

        if response.status_code != 202:
            return Response({'Error': 'Error sending email'})

        User.objects.filter(email=email).update(password=hashed_password)

        return Response({'message': f'Password resest email sent to {email}'})
    except Exception as e:
        print(str(e), 'errordan')
        return Response({message: str(e)})


@api_view(['GET'])
def get_me(request):
    bearer_token = request.headers.get('authorization')

    if bearer_token is None:
        return Response({'Error': 'Bearer Token required'})
    slice = bearer_token[7:]

    user = UserLoginTokens.objects.filter(access_token=slice).count()

    if user == 0 or user < 1:
        return Response({'Error': 'No user found'})
    att = UserLoginTokens.objects.filter(
        access_token=slice).values('user_id')

    obj = {}

    for val in att:
        obj['id'] = val['user_id']

    user = User.objects.filter(id=obj['id']).values(
        'first_name', 'last_name', 'email')

    user_obj = {}
    for val in user:
        user_obj = val

    return Response(user_obj)


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', get_tokens_for_user, name='token_obtain_pair'),
    path('refresh_token/', refresh_token, name='refresh_token'),
    path('twitter', twitter, name='twitter'),
    path('resetPassword/', reset_password, name='reset_password'),
    path('user/getMe/', get_me, name='get_me')
]

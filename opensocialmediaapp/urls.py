# """opensocialmediaapp URL Configuration

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/4.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# # from django.contrib import admin
# # from django.urls import path

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# # ]

# from django.urls import include, path
# from rest_framework import routers
# from opensocialmediaapp.api import views
# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# # Setup automatic URL routing
# # Additionally, we include login URLs for the browsable API.
# urlpatterns = [
#     path('', include(router.urls)),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
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

# from django.conf.urls import handler403, handler404, handler500, url


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'login', views.LoginViewSet)


@api_view(['GET'])
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

    refresh = RefreshToken.for_user(user[0])

    access = refresh.access_token
    saved_token = UserLoginTokens.objects.create(
        access_token=access, refresh_token=refresh, user_id=user_id)

    saved_token.save()
    # return Response({'Success': 'New user created'})

    return Response({
        'access': str(access),
        'refresh': str(refresh),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.data['refresh_token']
    user = UserLoginTokens.objects.filter(refresh_token=refresh_token)
    if not user:
        return Response({'Error': 'No user found with those details'})

    refresh = RefreshToken.for_user(user[0])
    access = refresh.access_token
    updated_token_user = UserLoginTokens.objects.update(access_token=access)

    return Response({'access': str(access)})


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('user/login_dan', views.UserViewSet.login_user_to_app_dan, name='enterprise')
    # path('testing123', views.TestUser.login_user_to_app_daniel)
    path('token/', get_tokens_for_user, name='token_obtain_pair'),
    path('refresh_token/', refresh_token, name='refresh_token')
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# from django.contrib.auth.models import User, Group
import time
import environ
from operator import itemgetter
from ..api.models import User, Instagram, UserLoginTokens
from rest_framework import viewsets
from .serializers import UserSerializer, InstagramSerializer
import logging
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import jwt
logger = logging.getLogger(__name__)
env = environ.Env()
environ.Env.read_env()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = 'id'
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        print('dannnn')
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def list(self, request, pk=None):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        print('called create')
        first_name, last_name, email, password = itemgetter(
            'first_name', 'last_name', 'email', 'password')(request.data)
        hashed_password = make_password(password)

        # first is password to check (req.body.password), 2nd is password in db
        # check = check_password(password, hashed_password)

        new_user = User.objects.create(
            first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        new_user.save()
        return Response({'Success': 'New user created'})

    @action(methods=['post'], detail=True)
    def update_password(self, request, pk):

        old_password = request.data['old_password']

        new_password = request.data['new_password']
        bearer_token = request.headers.get('authorization')
        slice = bearer_token[7:]
        user = UserLoginTokens.objects.filter(access_token=slice).count()

        if user == 0 or user < 1:
            return Response({'Error': 'No user found'})

        att = UserLoginTokens.objects.filter(
            access_token=slice).values('user_id')
        obj = {}

        for val in att:
            obj['id'] = val['user_id']

        if str(obj['id']) != pk:
            return Response({'Error': 'ID doesnt match'})

        user_to_update = User.objects.filter(id=pk).values('password')
        for att in user_to_update:
            obj['password'] = att['password']

        checked = check_password(old_password, obj['password'])

        if checked == False:
            return Response({'Error': 'Incorrect current password'})

        hashed_password = make_password(new_password)
        User.objects.filter(id=pk).update(password=hashed_password)

        return Response({'Success': 'Password successfully updated'})


class InstagramViewSet(viewsets.ModelViewSet):
    queryset = Instagram.objects.all()
    serializer_class = InstagramSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True)
    def get_daniel():
        print('hi')


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


def decodeJWT(token: str) -> dict:
    try:
        jwt_algorithm = env('algorithm')
        jwt_secret = env('secret')
        decoded_token = jwt.decode(
            token, jwt_secret, algorithms=[jwt_algorithm])
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except:
        return {}


class LoginViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = 'id'

    def create(self, request):
        return Response({'Success': 'Logged in'})

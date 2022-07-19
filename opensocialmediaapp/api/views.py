# from django.contrib.auth.models import User, Group
from operator import itemgetter
from ..api.models import User
from rest_framework import viewsets
from .serializers import UserSerializer
import logging
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = 'id'
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def list(self, request, pk=None):
        print('listing')
        print(request, 'request123')
        queryset = User.objects.all()
        print(queryset, 'dan123')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        first_name, last_name, email, password = itemgetter(
            'first_name', 'last_name', 'email', 'password')(request.data)
        hashed_password = make_password(password)

        # first is password to check (req.body.password), 2nd is password in db
        # check = check_password(password, hashed_password)

        new_user = User.objects.create(
            first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        new_user.save()
        return Response({'Success': 'New user created'})

    # @action(detail=True, methods=['post'], url_path=r'some-prefix/(?P<email>\w+)',)
    # def login_user_to_app_dan(self, request, pk=None):
    #     print('dan')
    #     return Response({'Success': 'New user created'})


# class TestUser():
#     @action(detail=True, methods=['post'])
#     def login_user_to_app_daniel(self, request, pk=None):
#         print('dan')
#         return Response({'Success': 'New user created'})

# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


class LoginViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = 'id'

    def create(self, request):
        print('called 213')
        return Response({'Success': 'Logged in'})

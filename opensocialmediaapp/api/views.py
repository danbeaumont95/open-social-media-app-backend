# from django.contrib.auth.models import User, Group
from ..api.models import User
from rest_framework import viewsets
from .serializers import UserSerializer
import logging
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        print('listing')
        queryset = User.objects.all()
        print(queryset, 'dan123')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer

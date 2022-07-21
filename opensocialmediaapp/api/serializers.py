

from rest_framework import serializers
import uuid
from django.db import models
# from django.contrib.auth.models import User
from ..api.models import User


class LowerCaseEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        return super().to_internal_value(data).lower()


class UserSerializer(serializers.ModelSerializer):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)
    email = LowerCaseEmailField(allow_blank=False)
    password = serializers.CharField(allow_blank=False)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password'
        ]
        read_only_fields = [
            'id'
        ]

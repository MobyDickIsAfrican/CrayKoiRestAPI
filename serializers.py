from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ['name', 'id']

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = ['title', 'id']

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Component
        fields = ['id', 'secondary_state', 'left', 'top', 'width', 'height', 'comp_id', 'parent']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
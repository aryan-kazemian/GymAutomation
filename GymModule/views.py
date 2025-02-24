from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GymUser, GymUserPayment, User
from django.contrib.auth import authenticate
from . import serializers


class GymUserAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            items = GymUser.objects.filter(gym_id=int(query))
            serializer = serializers.GymUserSerializer(items, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)


class GymUserPaymentSerializerAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            items = GymUserPayment.objects.filter(gym_user__gym_id=int(query))
            serializer = serializers.GymUserPaymentSerializer(items, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)

class UserSerializerAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            items = User.objects.filter(id=int(query))
            serializer = serializers.UserSerializer(items, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)

class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            # User exists and credentials are correct, return user info
            serializer = serializers.UserSerializer(user)
            return Response(serializer.data)
        else:
            # Authentication failed
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import User, GymUser, GymUserPayment, Logs
from .serializers import (UserSerializer, GymUserSerializer, GymUserEditSerializer,
                          GymUserPaymentSerializer, GymUserPaymentEditSerializer, LogsEditSerializer, LogsSerializer)
from rest_framework.pagination import PageNumberPagination


class UserAPIView(APIView):
    def post(self, request):
        """Handle user login."""
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve user information by ID."""
        user_id = request.GET.get('id')

        if user_id:
            user = get_object_or_404(User, id=int(user_id))
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'User ID is required'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Update user information by ID."""
        user_id = request.GET.get('id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_404_NOT_FOUND)

        user = get_object_or_404(User, id=int(user_id))
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class GymUserAPIView(APIView):
    def get(self, request):
        """Retrieve all gym users with optional pagination."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        page = request.GET.get('page', 1)
        item_perpage = request.GET.get('item_perpage', 10)

        if user_id:
            user = get_object_or_404(GymUser, id=int(user_id))
            serializer = GymUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = GymUser.objects.all()
        if gym_id:
            users = users.filter(gym_id=int(gym_id))

        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = int(item_perpage)
        result_page = paginator.paginate_queryset(users, request)
        serializer = GymUserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Create a new gym user if ?create=true is provided."""
        serializer = GymUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GymUserPaymentAPIView(APIView):
    def get(self, request):
        """Retrieve gym user payments with optional pagination."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        payment_id = request.GET.get('payment-id')
        page = request.GET.get('page', 1)
        item_perpage = request.GET.get('item_perpage', 10)

        if payment_id:
            payment = get_object_or_404(GymUserPayment, id=int(payment_id))
            serializer = GymUserPaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        payments = GymUserPayment.objects.all()
        if gym_id:
            payments = payments.filter(gym_user__gym_id=int(gym_id))
        elif user_id:
            payments = payments.filter(gym_user__id=int(user_id))

        paginator = PageNumberPagination()
        paginator.page_size = int(item_perpage)
        result_page = paginator.paginate_queryset(payments, request)
        serializer = GymUserPaymentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class LogsAPIView(APIView):
    def get(self, request):
        """Retrieve logs filtered by gym-user-id or gym-id with pagination."""
        gym_user_id = request.GET.get('gym-user-id')
        gym_id = request.GET.get('gym-id')
        page = request.GET.get('page', 1)
        item_perpage = request.GET.get('item_perpage', 10)

        logs = Logs.objects.all()
        if gym_user_id:
            logs = logs.filter(gym_user_id=int(gym_user_id))
        elif gym_id:
            logs = Logs.objects.filter(gym__id=int(gym_id))

        paginator = PageNumberPagination()
        paginator.page_size = int(item_perpage)
        result_page = paginator.paginate_queryset(logs, request)
        serializer = LogsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

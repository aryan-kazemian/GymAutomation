from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import User, GymUser, GymUserPayment, Logs
from datetime import timedelta, datetime
from django.utils.timezone import now
from .serializers import (
    UserSerializer, GymUserSerializer, GymUserEditSerializer,
    GymUserPaymentSerializer, GymUserPaymentEditSerializer,
    LogsEditSerializer, LogsSerializer
)


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


class CustomPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = int(request.GET.get('item_perpage', 10))
        return super().paginate_queryset(queryset, request, view)

class GymUserAPIView(APIView):
    def get(self, request):
        """Retrieve gym users with optional filters, pagination, count by gym ID, and filtering by recent join date."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        gym_user_count_id = request.GET.get('gym-user-counts-by-gym-id')
        joined_last_days = request.GET.get('joined-last-days')

        # Return gym user count
        if gym_user_count_id:
            count = GymUser.objects.filter(gym_id=int(gym_user_count_id)).count()
            return Response({"gym_user_count": count}, status=status.HTTP_200_OK)

        users = GymUser.objects.all()

        if gym_id:
            users = users.filter(gym_id=int(gym_id))

        if user_id:
            user = get_object_or_404(GymUser, id=int(user_id))
            return Response(GymUserSerializer(user).data, status=status.HTTP_200_OK)

        # Filter users who joined in the last X days and belong to a specific gym
        if joined_last_days and gym_id:
            try:
                days = int(joined_last_days)
                start_date = now() - timedelta(days=days)
                users = users.filter(join_date__gte=start_date, gym_id=int(gym_id))
            except ValueError:
                return Response({"error": "Invalid days format"}, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(users, request)
        return paginator.get_paginated_response(GymUserSerializer(result_page, many=True).data)


class GymUserPaymentAPIView(APIView):
    def get(self, request):
        """Retrieve gym user payments with optional filters and pagination."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        payment_id = request.GET.get('payment-id')

        payments = GymUserPayment.objects.all()
        if payment_id:
            payment = get_object_or_404(GymUserPayment, id=int(payment_id))
            return Response(GymUserPaymentSerializer(payment).data, status=status.HTTP_200_OK)
        if gym_id:
            payments = payments.filter(gym_user__gym_id=int(gym_id))
        if user_id:
            payments = payments.filter(gym_user__id=int(user_id))

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(payments, request)
        return paginator.get_paginated_response(GymUserPaymentSerializer(result_page, many=True).data)


class LogsAPIView(APIView):
    def get(self, request):
        """Retrieve logs filtered dynamically with pagination."""
        gym_user_id = request.GET.get('gym-user-id')
        gym_id = request.GET.get('gym-id')

        logs = Logs.objects.all()
        if gym_user_id:
            logs = logs.filter(gym_user_id=int(gym_user_id))
        if gym_id:
            logs = logs.filter(gym__id=int(gym_id))

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(logs, request)
        return paginator.get_paginated_response(LogsSerializer(result_page, many=True).data)

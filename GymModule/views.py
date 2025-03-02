from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, GymUser, GymUserPayment
from .serializers import (UserSerializer, GymUserSerializer, GymUserEditSerializer,
                          GymUserPaymentSerializer, GymUserPaymentEditSerializer)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GymUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all gym users by gym-id or a single gym user by user-id."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')

        if user_id:
            user = get_object_or_404(GymUser, id=int(user_id))
            serializer = GymUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if gym_id:
            users = GymUser.objects.filter(gym_id=int(gym_id))
            serializer = GymUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Provide either gym-id or user-id'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Edit a gym user's details."""
        user_id = request.GET.get('user-id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(GymUser, id=int(user_id))
        serializer = GymUserEditSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete a gym user by ID."""
        user_id = request.GET.get('user-id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(GymUser, id=int(user_id))
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        """Create a new gym user if ?create=true is provided."""
        create_flag = request.GET.get('create')

        if create_flag != 'true':
            return Response({'error': 'Invalid request for creation'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GymUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GymUserPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve payments based on gym-id, user-id, or a specific payment-id."""
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        payment_id = request.GET.get('payment-id')

        if payment_id:
            payment = get_object_or_404(GymUserPayment, id=int(payment_id))
            serializer = GymUserPaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if gym_id:
            payments = GymUserPayment.objects.filter(gym_user__gym_id=int(gym_id))
        elif user_id:
            payments = GymUserPayment.objects.filter(gym_user__id=int(user_id))
        else:
            return Response({'error': 'Provide either gym-id or user-id'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GymUserPaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new payment if ?create=true."""
        create_flag = request.GET.get('create')

        if create_flag != 'true':
            return Response({'error': 'Invalid request for creation'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required for payment creation'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gym_user = GymUser.objects.get(id=int(user_id))
        except GymUser.DoesNotExist:
            return Response({'error': 'Invalid Gym User ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GymUserPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym_user=gym_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Edit an existing payment by payment-id."""
        payment_id = request.GET.get('payment-id')
        if not payment_id:
            return Response({'error': 'Payment ID is required for editing'}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(GymUserPayment, id=int(payment_id))
        serializer = GymUserPaymentEditSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete a payment by payment-id."""
        payment_id = request.GET.get('payment-id')
        if not payment_id:
            return Response({'error': 'Payment ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(GymUserPayment, id=int(payment_id))
        payment.delete()
        return Response({'message': 'Payment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

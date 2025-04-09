from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from .models import User, GymUser, GymUserPayment, Logs, VipLocker
from django.db.models import Q
from datetime import timedelta, datetime
from django.utils.timezone import now
from .serializers import (
    UserSerializer, GymUserSerializer, GymUserEditSerializer,
    GymUserPaymentSerializer, GymUserPaymentEditSerializer,
    LogsEditSerializer, LogsSerializer, VipLockerSerializer
)


class UserAPIView(APIView):
    def post(self, request):
        """Handle user login or assign new vip locker numbers to a user by ID."""
        user_id = request.GET.get('id')
        vip_locker_numbers = request.data.get('vip_locker_numbers')

        if user_id and vip_locker_numbers is not None:
            user = get_object_or_404(User, id=int(user_id))

            # Normalize to list
            if isinstance(vip_locker_numbers, int):
                vip_locker_numbers = [vip_locker_numbers]

            for number in vip_locker_numbers:
                # Create new locker with the given number
                locker = VipLocker.objects.create(number=number)
                user.vip_locker_numbers.add(locker)

            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Default login behavior
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'User ID is required or invalid data'}, status=status.HTTP_400_BAD_REQUEST)

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
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        active_user_by_gym_id = request.GET.get('active-user-by-gym-id')

        if active_user_by_gym_id:
            active_users_count = GymUser.objects.filter(
                gym_id=int(active_user_by_gym_id),
                expiration_date__gte=timezone.now(),
            ).filter(
                Q(day_left__isnull=True) | Q(day_left__gt=0)
            ).count()

            return Response({'active_users': active_users_count}, status=status.HTTP_200_OK)

        if user_id:
            user = get_object_or_404(GymUser, id=int(user_id))
            return Response(GymUserSerializer(user).data, status=status.HTTP_200_OK)

        users = GymUser.objects.all()
        if gym_id:
            users = users.filter(gym_id=int(gym_id))

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(users, request)
        return paginator.get_paginated_response(GymUserSerializer(result_page, many=True).data)

    def post(self, request):
        serializer = GymUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
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
        user_id = request.GET.get('user-id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(GymUser, id=int(user_id))
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class GymUserPaymentAPIView(APIView):
    def get(self, request):
        gym_id = request.GET.get('gym-id')
        user_id = request.GET.get('user-id')
        payment_id = request.GET.get('payment-id')
        past_year_filter = request.GET.get('past-year-payments')

        use_pagination = True

        if payment_id:
            payment = get_object_or_404(GymUserPayment, id=int(payment_id))
            return Response(GymUserPaymentSerializer(payment).data, status=status.HTTP_200_OK)

        payments = GymUserPayment.objects.all()

        if past_year_filter == "1":
            one_year_ago = now() - timedelta(days=365)
            payments = payments.filter(payed_date__gte=one_year_ago)
            use_pagination = False


        if gym_id:
            payments = payments.filter(gym_user__gym_id=int(gym_id))
        if user_id:
            payments = payments.filter(gym_user__id=int(user_id))

        if use_pagination:
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(payments, request)
            return paginator.get_paginated_response(GymUserPaymentSerializer(result_page, many=True).data)

        else:
            return Response(GymUserPaymentSerializer(payments, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GymUserPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        payment_id = request.GET.get('payment-id')
        if not payment_id:
            return Response({'error': 'Payment ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(GymUserPayment, id=int(payment_id))
        serializer = GymUserPaymentEditSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogsAPIView(APIView):
    def get(self, request):
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

    def post(self, request):
        serializer = LogsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        log_id = request.GET.get('log-id')
        if not log_id:
            return Response({'error': 'Log ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        log = get_object_or_404(Logs, id=int(log_id))
        serializer = LogsEditSerializer(log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VipLockerAPIView(APIView):

    def get(self, request):
        gym_id = request.GET.get('gym_id')
        if not gym_id:
            return Response({"error": "gym_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=gym_id)
        vip_lockers = user.vip_locker_numbers.all()
        serializer = VipLockerSerializer(vip_lockers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        gym_id = request.GET.get('gym_id')
        if not gym_id:
            return Response({"error": "gym_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=gym_id)
        data = request.data
        numbers = data.get('number')

        if isinstance(numbers, list):
            created_lockers = []
            for number in numbers:
                locker, _ = VipLocker.objects.get_or_create(number=number)
                user.vip_locker_numbers.add(locker)
                created_lockers.append(locker)
            serializer = VipLockerSerializer(created_lockers, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif isinstance(numbers, int):
            locker, _ = VipLocker.objects.get_or_create(number=numbers)
            user.vip_locker_numbers.add(locker)
            serializer = VipLockerSerializer(locker)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid number format. Must be int or list of ints."},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        gym_id = request.GET.get('gym_id')
        locker_number = request.GET.get('locker_number')

        if not gym_id or not locker_number:
            return Response({"error": "gym_id and locker_number are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=gym_id)
        locker = get_object_or_404(VipLocker, number=int(locker_number))

        if locker not in user.vip_locker_numbers.all():
            return Response({"error": "Locker not assigned to this user"}, status=status.HTTP_404_NOT_FOUND)

        new_number = request.data.get('number')
        if not new_number:
            return Response({"error": "New locker number is required"}, status=status.HTTP_400_BAD_REQUEST)

        locker.number = new_number
        locker.save()
        return Response({"success": f"Locker updated to number {new_number}"}, status=status.HTTP_200_OK)

    def delete(self, request):
        gym_id = request.GET.get('gym_id')
        locker_number = request.GET.get('locker_number')

        if not gym_id or not locker_number:
            return Response({"error": "gym_id and locker_number are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=gym_id)
        locker = get_object_or_404(VipLocker, number=int(locker_number))

        if locker not in user.vip_locker_numbers.all():
            return Response({"error": "Locker not assigned to this user"}, status=status.HTTP_404_NOT_FOUND)

        user.vip_locker_numbers.remove(locker)
        locker.delete()
        return Response({"success": f"Locker #{locker_number} deleted"}, status=status.HTTP_204_NO_CONTENT)


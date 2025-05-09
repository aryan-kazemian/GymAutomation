from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import UserSerializer

User = get_user_model()


class UserAPIView(APIView):
    def get(self, request):
        filters = Q()
        filter_fields = [
            'id', 'is_admin', 'is_staff', 'creation_date', 'creation_time', 'full_name',
            'father_name', 'gender', 'birth_date', 'tel', 'mobile', 'education', 'job',
            'session_left', 'subscription_start_date', 'subscription_end_date'
        ]

        for field in filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        users = User.objects.filter(filters)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user_id = request.query_params.get('id')
        if not user_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = request.query_params.get('id')
        if not user_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

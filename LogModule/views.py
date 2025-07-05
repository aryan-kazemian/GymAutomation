import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
import base64
from math import ceil
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from .models import Log, GenMember
from .serializers import LogSerializer
from LockerModule.models import Locker

logger = logging.getLogger(__name__)

class LogAPIView(APIView):
    def get(self, request):
        log_id = request.query_params.get('id')  # <-- added this line at the top of the method

        # Pagination params
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # Use log_id if provided, else get all logs
        if log_id:
            logs_qs = Log.objects.filter(id=log_id).order_by('-id')
        else:
            logs_qs = Log.objects.all().order_by('-id')

        total_items = logs_qs.count()
        total_pages = ceil(total_items / limit) if total_items > 0 else 1

        # Calculate pagination slice
        start = (page - 1) * limit
        end = start + limit
        logs_page = logs_qs[start:end]

        # Prepare result list
        items = []

        for log in logs_page:
            member = log.user  # GenMember instance
            person = member.person if member else None

            # Locker linked to this person
            locker = None
            if person:
                locker = Locker.objects.filter(user=person).order_by('-id').first()

            # person_image base64 encode if exists
            if person and person.person_image:
                person_image_b64 = base64.b64encode(person.person_image).decode('utf-8')
            else:
                person_image_b64 = None

            item = {
                'id': log.id,
                'user': member.id if member else None,
                'full_name': person.full_name if person else log.full_name,
                'is_online': log.is_online,
                'entry_time': log.entry_time,
                'exit_time': log.exit_time,
                'role': member.role.role_desc if member and member.role else None,
                'sport': member.sport if member else None,
                'session_left': member.session_left if member else None,
                'membership_datetime': member.membership_datetime if member else None,
                'person_image': person_image_b64,
                'locker_number': locker.id if locker else None,
            }

            items.append(item)

        online_memebers = Log.objects.filter(is_online=True).count()

        response_data = {
            'total_items': total_items,
            'current_page': page,
            'total_pages': total_pages,
            'online_memebers': online_memebers,
            'items': items,
        }

        return Response(response_data)


    def post(self, request):
        user_id = request.data.get('user')
        if user_id is None:
            return Response({'user': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            get_object_or_404(GenMember, id=user_id)
        except Exception:
            return Response({'user': 'Invalid user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error saving Log: {e}", exc_info=True)
                return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        log_id = request.query_params.get('id')
        if not log_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log = Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LogSerializer(log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        log_id = request.query_params.get('id')
        if not log_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log = Log.objects.get(id=log_id)
            log.delete()
            return Response({'message': 'Log deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Log.DoesNotExist:
            return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)

import base64
import logging
from math import ceil

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Log
from .serializers import LogSerializer
from LockerModule.models import Locker
from UserModule.models import GenMember

logger = logging.getLogger(__name__)

class LogAPIView(APIView):
    def get(self, request):
        log_id = request.query_params.get('id')
        is_online_param = request.query_params.get('is_online')
        person_param = request.query_params.get('person')

        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

        logs_qs = Log.objects.all()

        if log_id:
            logs_qs = logs_qs.filter(id=log_id)

        if is_online_param is not None:
            if is_online_param == '1':
                logs_qs = logs_qs.filter(is_online=True)
            elif is_online_param == '0':
                logs_qs = logs_qs.filter(is_online=False)
            else:
                return Response({'error': 'Invalid is_online value. Use 1 or 0.'}, status=status.HTTP_400_BAD_REQUEST)

        if person_param is not None:
            try:
                person_id = int(person_param)
            except ValueError:
                return Response({'error': 'Invalid person ID'}, status=status.HTTP_400_BAD_REQUEST)
            logs_qs = logs_qs.filter(user__person__id=person_id)

        logs_qs = logs_qs.order_by('-id')

        total_items = logs_qs.count()
        total_pages = ceil(total_items / limit) if total_items > 0 else 1

        start = (page - 1) * limit
        end = start + limit
        logs_page = logs_qs[start:end]

        items = []

        for log in logs_page:
            member = log.user
            person = member.person if member else None

            locker = None
            if person:
                locker = Locker.objects.filter(user=person).order_by('-id').first()

            if person and person.person_image:
                person_image_b64 = base64.b64encode(person.person_image).decode('utf-8')
            else:
                person_image_b64 = None

            item = {
                'id': log.id,
                'user': member.id if member else None,
                'person_id': person.id if person else None,
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

        online_members = Log.objects.filter(is_online=True).count()

        response_data = {
            'total_items': total_items,
            'current_page': page,
            'total_pages': total_pages,
            'online_members': online_members,
            'items': items,
        }

        return Response(response_data)

    def post(self, request):
        user_id = request.data.get('user')
        if user_id is None:
            return Response({'user': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = get_object_or_404(GenMember, id=user_id)
        except Exception:
            return Response({'user': 'Invalid user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            try:
                log = serializer.save()
                if member.session_left is not None:
                    if member.session_left > 0:
                        member.session_left -= 1
                    else:
                        member.session_left = None
                    member.save()
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

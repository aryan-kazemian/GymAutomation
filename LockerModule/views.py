from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Locker
from .serializers import LockerSerializer
import math

class LockerAPIView(APIView):
    def get(self, request):
        locker_id = request.query_params.get('id')
        if locker_id:
            locker = Locker.objects.filter(id=locker_id).first()
            if not locker:
                return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = LockerSerializer(locker)
            return Response(serializer.data)

        filters = Q()
        for field in ['is_vip', 'is_open', 'user', 'full_name']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        lockers = Locker.objects.filter(filters)

        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

        total_items = lockers.count()
        total_pages = math.ceil(total_items / limit)
        start = (page - 1) * limit
        end = start + limit
        paginated_lockers = lockers[start:end]

        serializer = LockerSerializer(paginated_lockers, many=True)
        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'data': serializer.data
        })

    def post(self, request):
        close_all_non_vip = request.query_params.get('close_all_non_vip')
        open_all_non_vip = request.query_params.get('open_all_non_vip')
        multiple_creation = request.query_params.get('multiple_creation')

        if close_all_non_vip == '1':
            Locker.objects.filter(is_vip=False).update(is_open=False)
            return Response({'message': 'All non-VIP lockers have been closed.'}, status=status.HTTP_200_OK)

        if open_all_non_vip == '1':
            Locker.objects.filter(is_vip=False).update(is_open=True)
            return Response({'message': 'All non-VIP lockers have been opened.'}, status=status.HTTP_200_OK)

        if multiple_creation == '1':
            locker_count = request.data.get('locker_count')
            vip_count = request.data.get('vip_count', 0)

            try:
                locker_count = int(locker_count)
                vip_count = int(vip_count)
                if locker_count < 1 or vip_count < 0 or vip_count > locker_count:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({'error': 'Invalid locker_count or vip_count'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine available 'number' values starting from 1
            existing_numbers = set(Locker.objects.values_list('number', flat=True))
            next_number = 1
            assigned_numbers = []

            while len(assigned_numbers) < locker_count:
                if next_number not in existing_numbers:
                    assigned_numbers.append(next_number)
                next_number += 1

            # Create locker_count lockers, last vip_count are VIP
            new_lockers = []
            for i in range(locker_count):
                is_vip = i >= (locker_count - vip_count)
                locker = Locker(
                    is_vip=is_vip,
                    is_open=False,
                    log=None,
                    user=None,
                    full_name=None,
                    number=assigned_numbers[i]
                )
                new_lockers.append(locker)

            Locker.objects.bulk_create(new_lockers)

            return Response({'message': f'{locker_count} lockers created successfully, with {vip_count} VIP.'}, status=status.HTTP_201_CREATED)

        # Default behavior: create a single locker from request data
        serializer = LockerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        locker_id = request.query_params.get('id')
        if not locker_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        locker = Locker.objects.filter(id=locker_id).first()
        if not locker:
            return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockerSerializer(locker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        locker_id = request.query_params.get('id')
        if not locker_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        locker = Locker.objects.filter(id=locker_id).first()
        if not locker:
            return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)

        locker.delete()
        return Response({'message': 'Locker deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

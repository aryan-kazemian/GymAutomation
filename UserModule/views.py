from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import GenShift, SecUser, GenPerson, GenPersonRole, GenMember, GenMembershipType
from .serializers import (
    GenShiftSerializer, SecUserSerializer, GenPersonSerializer, GenPersonRoleSerializer,
    GenMemberSerializer, GenMembershipTypeSerializer
)


class DynamicAPIView(APIView):

    def get_model(self, action):
        if action == 'shift':
            return GenShift
        elif action == 'user':
            return SecUser
        elif action == 'person':
            return GenPerson
        elif action == 'role':
            return GenPersonRole
        elif action == 'member':
            return GenMember
        elif action == 'membership_type':
            return GenMembershipType
        elif action == 'pool':
            return GenMember  # ✅ Added pool mapping
        return None

    def get_serializer_class(self, model):
        if model == GenShift:
            return GenShiftSerializer
        elif model == SecUser:
            return SecUserSerializer
        elif model == GenPerson:
            return GenPersonSerializer
        elif model == GenPersonRole:
            return GenPersonRoleSerializer
        elif model == GenMember:
            return GenMemberSerializer
        elif model == GenMembershipType:
            return GenMembershipTypeSerializer
        return None

    def get_serializer(self, *args, **kwargs):
        if not hasattr(self, 'serializer_class') or self.serializer_class is None:
            raise AssertionError("serializer_class must be set before calling get_serializer()")
        return self.serializer_class(*args, **kwargs)

    def get(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)

        if action == 'pool':
            queryset = GenMember.objects.select_related('shift', 'person')

            filters = Q()
            for key, value in request.query_params.items():
                if key not in ['action', 'page', 'limit', 'order_by']:
                    filters &= Q(**{key: value})

            queryset = queryset.filter(filters, is_single_settion=True)

            order_by = request.query_params.get('order_by')
            if order_by == 'latest':
                queryset = queryset.order_by('-creation_datetime')
            elif order_by == 'earlier':
                queryset = queryset.order_by('creation_datetime')

            try:
                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))
            except ValueError:
                return Response({'error': 'Invalid pagination values'}, status=status.HTTP_400_BAD_REQUEST)

            total_items = queryset.count()
            total_pages = (total_items + limit - 1) // limit

            start = (page - 1) * limit
            end = start + limit
            paginated_queryset = queryset[start:end]

            data = []
            for member in paginated_queryset:
                data.append({
                    'price': member.price,
                    'shift_description': member.shift.shift_desc if member.shift else None,
                    'creation_datetime': member.creation_datetime,
                    'full_name': member.person.full_name if member.person else None
                })

            return Response({
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'items': data
            })

        # Rest of your existing get logic untouched
        filters = Q()
        object_id = request.query_params.get('id')

        if object_id:
            filters &= Q(id=object_id)

        for key, value in request.query_params.items():
            if key not in ['action', 'id', 'page', 'limit', 'order_by']:
                if key == 'full_name':
                    filters &= Q(full_name__icontains=value)
                else:
                    filters &= Q(**{key: value})

        queryset = model.objects.filter(filters)

        order_by = request.query_params.get('order_by')
        use_creation_field = action in ['person', 'user', 'member']

        if use_creation_field:
            if order_by == 'latest':
                queryset = queryset.order_by('-creation_datetime')
            elif order_by == 'earlier':
                queryset = queryset.order_by('creation_datetime')
        else:
            if order_by == 'latest':
                queryset = queryset.order_by('-id')
            elif order_by == 'earlier':
                queryset = queryset.order_by('id')

        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            return Response({'error': 'Invalid pagination values'}, status=status.HTTP_400_BAD_REQUEST)

        total_items = queryset.count()
        total_pages = (total_items + limit - 1) // limit

        start = (page - 1) * limit
        end = start + limit
        paginated_queryset = queryset[start:end]

        serializer = self.get_serializer(paginated_queryset, many=True)
        data = serializer.data

        # Extra for person
        if action == 'person':
            person_ids = [item['id'] for item in data]
            members = GenMember.objects.filter(person_id__in=person_ids).select_related('role').order_by('-creation_datetime')
            member_map = {}
            for member in members:
                pid = member.person_id
                if pid not in member_map:
                    member_map[pid] = {
                        'role': member.role.role_desc if member.role else None,
                        'sport': member.sport,
                        'session_left': member.session_left,
                        'subscription_end_date': member.end_date,
                    }
            for item in data:
                extra = member_map.get(item['id'], {})
                item['role'] = extra.get('role')
                item['sport'] = extra.get('sport')
                item['session_left'] = extra.get('session_left')
                item['subscription_end_date'] = extra.get('subscription_end_date')

        # Extra for member
        if action == 'member':
            person_ids = [item.get('person') for item in data if item.get('person')]
            persons = GenPerson.objects.filter(id__in=person_ids).values('id', 'full_name')
            person_map = {p['id']: p['full_name'] for p in persons}
            for item in data:
                person_id = item.get('person')
                item['full_name'] = person_map.get(person_id)

        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items': data
        })

    def post(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)

        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)

        # Custom behavior for 'pool' action
        if action == 'pool':
            data = request.data.copy()

            # Force is_single_settion to True
            data['is_single_settion'] = True

            # Set session_left to 1
            data['session_left'] = 1

            # Handle full_name → create GenPerson if full_name exists
            full_name = data.pop('full_name', None)
            if full_name:
                existing_person_ids = set(GenPerson.objects.values_list('id', flat=True))
                new_person_id = 1
                while new_person_id in existing_person_ids:
                    new_person_id += 1
                person = GenPerson.objects.create(id=new_person_id, full_name=full_name)
                data['person'] = person.id

            # Generate unique ID for GenMember
            if 'id' not in data or data['id'] in [None, '']:
                existing_ids = set(GenMember.objects.values_list('id', flat=True))
                new_id = 1
                while new_id in existing_ids:
                    new_id += 1
                data['id'] = new_id
            else:
                try:
                    base_id = int(data['id'])
                except ValueError:
                    return Response({'error': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

                while GenMember.objects.filter(id=base_id).exists():
                    base_id += 1
                data['id'] = base_id

            serializer = GenMemberSerializer(data=data)
            if serializer.is_valid():
                member = serializer.save()

                # Set membership_datetime to exact creation time
                member.membership_datetime = member.creation_datetime.strftime('%Y-%m-%d %H:%M:%S')
                member.save(update_fields=['membership_datetime'])

                return Response(GenMemberSerializer(member).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Default behavior for all other actions (untouched)
        if action == 'pool':
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()

        if 'id' not in data or data['id'] in [None, '']:
            existing_ids = set(model.objects.values_list('id', flat=True))
            new_id = 1
            while new_id in existing_ids:
                new_id += 1
            data['id'] = new_id
        else:
            try:
                base_id = int(data['id'])
            except ValueError:
                return Response({'error': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

            while model.objects.filter(id=base_id).exists():
                base_id += 1
            data['id'] = base_id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model or action == 'pool':
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        object_id = request.query_params.get('id')
        if not object_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = model.objects.get(id=object_id)
        except model.DoesNotExist:
            return Response({'error': f'{action} not found.'}, status=status.HTTP_404_NOT_FOUND)

        self.serializer_class = self.get_serializer_class(model)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        action = request.query_params.get("action")
        model = self.get_model(action)
        if not model or action == 'pool':
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)

        object_id = request.query_params.get("id") or request.data.get("id")
        if not object_id:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = model.objects.get(id=object_id)
            obj.delete()
            return Response({"detail": f"{action} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({"detail": f"{action} not found."}, status=status.HTTP_404_NOT_FOUND)
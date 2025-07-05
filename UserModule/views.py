from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import GenShift, SecUser, GenPerson, GenPersonRole, GenMember, GenMembershipType
from .serializers import (
    GenShiftSerializer, SecUserSerializer, GenPersonSerializer, GenPersonRoleSerializer,
    GenMemberSerializer, GenMembershipTypeSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class AuthenticationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        action = request.GET.get("action")

        if action == "login":
            print("login")
            return self.login(request)
        elif action == "logout":
            print("logout")
            return self.logout(request)
        else:
            return Response({"error": "Invalid action. Use ?action=login or ?action=logout"}, status=400)

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=400)

        try:
            user = SecUser.objects.get(username=username, password=password, is_active=True)
        except SecUser.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=401)

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        return Response({"message": "Login successful", "user_id": user.id})

    def logout(self, request):
        request.session.flush()
        return Response({"message": "Logout successful"})


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
        # This method overrides DRF's get_serializer to create the serializer instance correctly
        if not hasattr(self, 'serializer_class') or self.serializer_class is None:
            raise AssertionError("serializer_class must be set before calling get_serializer()")
        return self.serializer_class(*args, **kwargs)

    def get(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)

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
        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items': serializer.data
        })

    def post(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)

        data = request.data.copy()

        # If id is not manually set, auto-assign the next free one
        if 'id' not in data or data['id'] in [None, '']:
            # Use the lowest unused ID starting from 1
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
        if not model:
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

        if not model:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = self.get_serializer_class(model)  # ✅ Fix added here

        object_id = request.query_params.get("id") or request.data.get("id")
        if not object_id:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = model.objects.get(id=object_id)
            obj.delete()
            return Response({"detail": f"{action} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({"detail": f"{action} not found."}, status=status.HTTP_404_NOT_FOUND)

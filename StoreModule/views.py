# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math

from .models import StoreConfiguration, Category, Product, Order
from .serializers import (
    StoreConfigurationSerializer,
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
)


class BaseAPIView(APIView):
    """Base class with pagination + id handling"""

    model = None
    serializer_class = None
    filter_fields = []

    def build_filters(self, request):
        """Override this in subclasses if needed"""
        filters = Q()
        for field in self.filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})
        return filters

    def get(self, request):
        obj_id = request.query_params.get("id")
        if obj_id:
            instance = self.model.objects.filter(id=obj_id).first()
            if not instance:
                return Response({"error": f"{self.model.__name__} not found"}, status=404)
            serializer = self.serializer_class(instance)
            return Response(serializer.data)

        filters = self.build_filters(request)
        queryset = self.model.objects.filter(filters)

        # Pagination
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({"error": "Invalid pagination parameters"}, status=400)

        total_items = queryset.count()
        total_pages = math.ceil(total_items / limit) if total_items else 1
        start = (page - 1) * limit
        end = start + limit
        paginated = queryset[start:end]

        serializer = self.serializer_class(paginated, many=True)
        return Response({
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "data": serializer.data
        })

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        obj_id = request.query_params.get("id")
        if not obj_id:
            return Response({"error": "ID query param required for PATCH"}, status=400)

        instance = self.model.objects.filter(id=obj_id).first()
        if not instance:
            return Response({"error": f"{self.model.__name__} not found"}, status=404)

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        obj_id = request.query_params.get("id")
        if not obj_id:
            return Response({"error": "ID query param required for DELETE"}, status=400)

        instance = self.model.objects.filter(id=obj_id).first()
        if not instance:
            return Response({"error": f"{self.model.__name__} not found"}, status=404)

        instance.delete()
        return Response({"message": f"{self.model.__name__} deleted successfully"}, status=204)


# ---- Specific API Views ----

class StoreConfigurationAPIView(BaseAPIView):
    model = StoreConfiguration
    serializer_class = StoreConfigurationSerializer
    filter_fields = ["name", "is_active"]

    def build_filters(self, request):
        filters = super().build_filters(request)
        gym_id = request.query_params.get("gym_id")
        if gym_id:
            filters &= Q(gym_id=gym_id)
        return filters


class CategoryAPIView(BaseAPIView):
    model = Category
    serializer_class = CategorySerializer
    filter_fields = ["store", "is_active"]

    def build_filters(self, request):
        filters = super().build_filters(request)
        gym_id = request.query_params.get("gym_id")
        if gym_id:
            filters &= Q(store__gym_id=gym_id)
        return filters


class ProductAPIView(BaseAPIView):
    model = Product
    serializer_class = ProductSerializer
    filter_fields = ["category", "store", "is_available"]

    def build_filters(self, request):
        filters = super().build_filters(request)
        gym_id = request.query_params.get("gym_id")
        if gym_id:
            filters &= Q(store__gym_id=gym_id)
        return filters


class OrderAPIView(BaseAPIView):
    model = Order
    serializer_class = OrderSerializer
    filter_fields = ["status", "payment_method", "customer_name"]



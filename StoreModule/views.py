from rest_framework import viewsets
from .models import StoreConfiguration, Category, Product, Order
from .serializers import StoreConfigurationSerializer, CategorySerializer, ProductSerializer, OrderSerializer

class StoreConfigurationViewSet(viewsets.ModelViewSet):
    queryset = StoreConfiguration.objects.all()
    serializer_class = StoreConfigurationSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

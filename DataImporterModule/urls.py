from django.urls import path
from .views import DataImportFromJsonConfigAPIView, DataImportProgressAPIView

urlpatterns = [
    path('import-initial-data/', DataImportFromJsonConfigAPIView.as_view(), name='import-initial-data'),
    path('import-progress/', DataImportProgressAPIView.as_view(), name='import-progress'),
]

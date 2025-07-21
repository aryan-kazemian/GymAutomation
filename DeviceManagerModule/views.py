from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Device
from .serializers import DeviceSerializer

class DeviceAPIView(APIView):

    def get(self, request):
        valid_fields = {field.name for field in Device._meta.fields}
        filters = {k: v for k, v in request.query_params.items() if k in valid_fields}
        devices = Device.objects.filter(**filters)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        device_id = request.query_params.get('id')
        if not device_id:
            return Response({"error": "Missing 'id' in query parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        device_id = request.query_params.get('id')
        if not device_id:
            return Response({"error": "Missing 'id' in query parameters."}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = Device.objects.filter(id=device_id).delete()
        if deleted == 0:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

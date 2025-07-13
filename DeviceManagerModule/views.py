from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Device
from .serializers import DeviceSerializer

class DeviceAPIView(APIView):

    def get(self, request):
        filters = {k: v for k, v in request.query_params.items() if k in [f.name for f in Device._meta.fields]}
        devices = Device.objects.filter(**filters)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        device_id = request.query_params.get('id')
        if not device_id:
            return Response({"error": "Missing 'id' in query parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

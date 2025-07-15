from django.db import models

# Create your models here.

class Device(models.Model):
    deviceId = models.CharField(max_length=100, blank=True, null=True)
    deviceType = models.CharField(max_length=200, blank=True, null=True)
    deviceGroup = models.CharField(max_length=100, blank=True, null=True)
    deviceName = models.CharField(max_length=100, blank=True, null=True)
    devicePort = models.CharField(max_length=100, blank=True, null=True)
    deviceIP = models.CharField(max_length=100, blank=True, null=True)
    baudRate = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=100, blank=True, null=True)
    dataBits = models.CharField(max_length=100, blank=True, null=True)
    stopBits = models.CharField(max_length=100, blank=True, null=True)
    timeout = models.CharField(max_length=100, blank=True, null=True)
    protocol = models.CharField(max_length=100, blank=True, null=True)

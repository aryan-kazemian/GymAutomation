from django.db import models

# Create your models here.


class Device(models.Model):
    deviceId = models.CharField(max_length=100)
    deviceType = models.CharField(max_length=200)
    deviceGroup = models.CharField(max_length=100)
    deviceName = models.CharField(max_length=100)
    devicePort = models.CharField(max_length=100)
    deviceIP = models.CharField(max_length=100)
    baudRate = models.CharField(max_length=100)
    priority = models.CharField(max_length=100)
    dataBits = models.CharField(max_length=100)
    stopBits = models.CharField(max_length=100)
    timeout = models.CharField(max_length=100)
    protocol = models.CharField(max_length=100)
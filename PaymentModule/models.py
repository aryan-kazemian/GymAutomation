from django.db import models
from UserModule.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    paid_method = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Payment by {self.full_name or self.user_id} on {self.payment_date}"

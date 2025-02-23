from django.contrib import admin
from .models import User, GymPayment, GymUserPayment, GymUser

from GymModule.models import User

# Register your models here.

admin.site.register(User)
admin.site.register(GymPayment)
admin.site.register(GymUser)
admin.site.register(GymUserPayment)



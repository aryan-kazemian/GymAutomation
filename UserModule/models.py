from django.contrib.auth.models import AbstractUser
from django.db import models

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

SHIFT_CHOICES = [
    ('men', 'Men'),
    ('women', 'Women'),
]

class User(AbstractUser):
    is_admin = models.BooleanField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)
    creation_time = models.TimeField(auto_now_add=True)

    full_name = models.CharField(max_length=200, null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    national_code = models.CharField(max_length=20, null=True, blank=True)
    nidentity = models.CharField(max_length=20, null=True, blank=True)

    person_image = models.ImageField(upload_to='users/images/', null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='users/thumbnails/', null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    education = models.CharField(max_length=100, null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)

    has_insurance = models.BooleanField(null=True, blank=True)
    insurance_no = models.CharField(max_length=50, null=True, blank=True)
    ins_start_date = models.DateField(null=True, blank=True)
    ins_end_date = models.DateField(null=True, blank=True)

    paddress = models.TextField(null=True, blank=True)
    has_parrent = models.BooleanField(null=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)

    modifier = models.CharField(max_length=100, null=True, blank=True)
    modification_time = models.DateTimeField(null=True, blank=True)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    session_left = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.full_name or self.first_name + ' ' + self.last_name}"

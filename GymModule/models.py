from django.db import models
from django.contrib.auth.models import AbstractUser, User
from datetime import timedelta


class User(AbstractUser):
    gym_name = models.CharField(max_length=255, null=True, blank=True)
    gym_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    use_day_left = models.BooleanField(default=False)
    is_gym_manager = models.BooleanField(default=True)
    locker_count = models.IntegerField(default=60)
    vip_locker_count = models.IntegerField(default=20)
    image = models.ImageField(upload_to='gym-images/', null=True, blank=True)

    def update_expiration_date(self, subscription_duration):
        # Duration map for adding time
        duration_map = {
            '6_months': timedelta(days=180),
            '1_year': timedelta(days=365),
            '2_years': timedelta(days=730),
            '3_years': timedelta(days=1095),
        }
        self.expiration_date += duration_map.get(subscription_duration, timedelta(days=365))
        self.save()

class GymPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payed_amount = models.CharField(max_length=120)
    payed_date = models.DateTimeField(auto_now_add=True)
    subscription_duration = models.CharField(
        max_length=20,
        choices=[
            ('6_months', '6 months'),
            ('1_year', '1 year'),
            ('2_years', '2 years'),
            ('3_years', '3 years'),
        ],
        default='1_year'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            super(GymPayment, self).save(*args, **kwargs)
            self.user.update_expiration_date(self.subscription_duration)
        else:
            super(GymPayment, self).save(*args, **kwargs)

class GymUser(models.Model):
    gym = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    family = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    nation_cod = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    day_left = models.IntegerField(default=0)
    started_payment_date = models.DateTimeField(null=True, blank=True)
    fingerprint = models.BinaryField(null=True, blank=True)
    face_image = models.ImageField(upload_to='faces/', null=True, blank=True)
    face_binary = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    locker_number= models.IntegerField(null=True, blank=True)
    user_state = models.CharField(
        max_length=40,
        choices=[
            ('vip', 'vip'),
            ('normal', 'normal'),
        ],
        default='vip'
    )
    biometric_type = models.CharField(
        max_length=40,
        choices=[
            ('finger_print', 'finger print'),
            ('face_scan', 'face scan'),
        ],
         null=True
    )

    def update_expiration_date(self, subscription_duration, days):
        duration_map = {
            '1_months': timedelta(days=30),
            '2_months': timedelta(days=60),
            '3_months': timedelta(days=90),
            '6_months': timedelta(days=180),
            '9_months': timedelta(days=270),
            '1_year': timedelta(days=365),
            '2_year': timedelta(days=730),
        }
        self.expiration_date += duration_map.get(subscription_duration, timedelta(days=365))
        if days != 0:
            self.day_left += days
        self.save()

class GymUserPayment(models.Model):
    gym_user = models.ForeignKey(GymUser, on_delete=models.CASCADE)
    payed_amount = models.CharField(max_length=120)
    payed_date = models.DateTimeField(auto_now_add=True)
    subscription_duration = models.CharField(
        max_length=20,
        choices=[
            ('1_months', '1 months'),
            ('2_months', '2 months'),
            ('3_months', '3 months'),
            ('6_months', '6 months'),
            ('9_months', '9 months'),
            ('1_year', '1 year'),
            ('2_year', '2 year'),
        ],
        default='1_months'
    )
    subscription_days = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('card-to-card', 'card to card'),
            ('cash', 'cash'),
            ('pos_machine', 'pos machine'),
        ],
        default='pos_machine'
    )
    payment_state = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'paid'),
            ('waiting', 'waiting'),
            ('not-paid', 'not paid'),
        ],
        default='waiting'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.subscription_days:
                self.gym_user.update_expiration_date(self.subscription_duration, self.subscription_days)
            else:
                self.gym_user.update_expiration_date(self.subscription_duration, 0)

            self.gym_user.started_payment_date = self.payed_date

        super().save(*args, **kwargs)
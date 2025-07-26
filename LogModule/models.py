from django.db import models
from django.utils.timezone import now
from LockerModule.models import Locker

class Log(models.Model):
    user = models.ForeignKey('UserModule.GenMember', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    is_online = models.BooleanField(default=True)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_is_online = self.is_online  # store original value when loaded

    def save(self, *args, **kwargs):
        # Set exit time only once when going offline
        if not self.is_online and self.exit_time is None:
            self.exit_time = now()

        # 🔥 Detect change from True -> False
        if self._original_is_online and not self.is_online:
            person_id = self.user.person.id if self.user and self.user.person else None
            if person_id:
                locker = Locker.objects.filter(user_id=person_id).first()
                if locker and not locker.is_vip:
                    locker.user = None
                    locker.save()

        super().save(*args, **kwargs)
        self._original_is_online = self.is_online  # update after save

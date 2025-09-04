from django.db import models

class DataImportProgress(models.Model):
    task_name = models.CharField(max_length=100, unique=True)
    total_steps = models.IntegerField(default=0)
    current_step = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='pending')

    def progress_percent(self):
        if self.total_steps > 0:
            percent = int((self.current_step / self.total_steps) * 100)
            return max(0, min(100, percent))  # clamp 0–100
        return 0

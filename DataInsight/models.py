from django.db import models
from django.apps import apps


class ClubStats(models.Model):
    # Active members count
    active_members = models.IntegerField(null=True)

    # % change in active members vs previous month (int, can be negative)
    active_members_change_pct = models.IntegerField(null=True)

    # New members today
    new_members_today = models.IntegerField(null=True)

    # % change in new members vs yesterday
    new_members_change_pct = models.IntegerField(null=True)

    # Average daily attendance of members
    avg_daily_attendance = models.FloatField(null=True)

    # Retention rate of members (percentage)
    retention_rate_pct = models.IntegerField(null=True)

    # % change in retention rate vs last 6 months (can be negative)
    retention_change_pct = models.IntegerField(null=True)

    # Top 3 popular sports and counts of members who practice them, stored as JSON for flexibility
    # Example format:
    # [
    #     {"name": "Soccer", "count": 50, "percentage": 25.0},
    #     {"name": "Basketball", "count": 40, "percentage": 20.0},
    #     {"name": "Tennis", "count": 30, "percentage": 15.0}
    # ]
    top_sports_stats = models.JSONField(null=True)

    # Top 3 attendance hours to club with counts and average hours, stored as JSON for flexibility
    # Example format:
    # [
    #     {"hour_range": "6-7 PM", "count": 50, "avg_hours": 1.2},
    #     {"hour_range": "7-8 PM", "count": 40, "avg_hours": 1.0},
    #     {"hour_range": "5-6 PM", "count": 30, "avg_hours": 0.8}
    # ]
    top_attendance_hours = models.JSONField(null=True)

    # Attendance by weekday and count, stored as JSON field for flexibility
    # Example: {'Monday': 150, 'Tuesday': 130, ...}
    attendance_by_weekday = models.JSONField(null=True)

    # Monthly new membership trends, e.g. {'Shahrivar': 12, 'Mordad': 20}
    membership_trends = models.JSONField(default=dict, blank=True)

    # Members count by age groups
    # Structure: {'under_18': int, '18_to_25': int, '26_to_35': int, 'over_35': int}
    age_groups = models.JSONField(default=dict, blank=True)

    # Date for this stats entry
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"ClubStats for {self.date_recorded}"


class MemberSubLog(models.Model):
    member = models.ForeignKey("UserModule.GenMember", on_delete=models.SET_NULL, null=True)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


from django.db import models

class ClubStats(models.Model):
    # Active members count
    active_members = models.IntegerField()

    # % change in active members vs previous month (int, can be negative)
    active_members_change_pct = models.IntegerField()

    # New members today
    new_members_today = models.IntegerField()

    # % change in new members vs yesterday
    new_members_change_pct = models.IntegerField()

    # Average daily attendance of members
    avg_daily_attendance = models.IntegerField()

    # % change in avg daily attendance vs yesterday
    attendance_change_pct = models.IntegerField()

    # Retention rate of members (percentage)
    retention_rate_pct = models.IntegerField()

    # % change in retention rate vs last 6 months (can be negative)
    retention_change_pct = models.IntegerField()

    # Top 3 popular sports and counts of members who practice them
    # For each: sport name, count, percentage of total members practicing that sport
    top1_sport_name = models.CharField(max_length=100)
    top1_sport_count = models.IntegerField()
    top1_sport_pct = models.FloatField()

    top2_sport_name = models.CharField(max_length=100)
    top2_sport_count = models.IntegerField()
    top2_sport_pct = models.FloatField()

    top3_sport_name = models.CharField(max_length=100)
    top3_sport_count = models.IntegerField()
    top3_sport_pct = models.FloatField()

    # Max attendance hours to club (e.g. '6-7 PM') for top 3 time slots
    top1_attendance_hour = models.CharField(max_length=20)
    top1_attendance_count = models.IntegerField()
    top1_attendance_avg_hours = models.FloatField()

    top2_attendance_hour = models.CharField(max_length=20)
    top2_attendance_count = models.IntegerField()
    top2_attendance_avg_hours = models.FloatField()

    top3_attendance_hour = models.CharField(max_length=20)
    top3_attendance_count = models.IntegerField()
    top3_attendance_avg_hours = models.FloatField()

    # Attendance by weekday and count, stored as JSON field for flexibility
    # Example: {'Monday': 150, 'Tuesday': 130, ...}
    attendance_by_weekday = models.JSONField()

    # Average attendance hours by weekday, also JSON
    # Example: {'Monday': 2.5, 'Tuesday': 1.8, ...}
    avg_hours_by_weekday = models.JSONField()

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

